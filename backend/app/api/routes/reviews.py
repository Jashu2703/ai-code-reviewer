import hmac
import hashlib
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from loguru import logger
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.review import Review
from app.schemas import ReviewRequest, ReviewOut
from app.services.agents.orchestrator import run_review_pipeline
from app.services.github_service import get_pr_diff, get_pr_info, verify_webhook_signature
from app.services.mlflow_tracker import track_review

router = APIRouter()


def run_review_background(
    db: Session,
    review_id: int,
    diff_text: str,
    pr_number: int,
    pr_title: str,
    pr_author: str,
    repo_name: str,
    pr_url: str,
):
    """Run review pipeline in background and save results."""
    try:
        # Run the LangGraph pipeline
        result = run_review_pipeline(
            diff_text=diff_text,
            pr_number=pr_number,
            pr_title=pr_title,
            pr_author=pr_author,
            repo_name=repo_name,
            pr_url=pr_url,
        )

        # Track in MLflow
        mlflow_run_id = track_review(result, review_id)

        # Update DB
        review = db.query(Review).filter(Review.id == review_id).first()
        if review:
            review.status = result.get("status", "completed")
            review.overall_score = result.get("overall_score")
            review.severity = result.get("severity", "low")
            review.issues = result.get("issues", [])
            review.suggestions = result.get("suggestions", [])
            review.security_issues = result.get("security_issues", [])
            review.performance_issues = result.get("performance_issues", [])
            review.summary = result.get("summary", "")
            review.analyzer_output = result.get("analyzer_output")
            review.reviewer_output = result.get("reviewer_output")
            review.similar_issues = result.get("similar_issues", [])
            review.lines_added = result.get("lines_added", 0)
            review.lines_removed = result.get("lines_removed", 0)
            review.files_changed = result.get("files_changed", [])
            review.posted_to_github = result.get("posted_to_github", 0)
            review.mlflow_run_id = mlflow_run_id
            review.completed_at = datetime.utcnow()
            db.commit()
            logger.info(f"Review {review_id} saved to DB")

    except Exception as e:
        logger.error(f"Background review failed: {e}")
        review = db.query(Review).filter(Review.id == review_id).first()
        if review:
            review.status = "failed"
            review.summary = str(e)
            db.commit()


@router.post("/trigger", response_model=ReviewOut)
def trigger_review(
    data: ReviewRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger a PR review."""
    diff_text = data.diff_text
    pr_info = None

    if not diff_text:
        diff_text = get_pr_diff(data.repo_name, data.pr_number)
        if not diff_text:
            raise HTTPException(status_code=422, detail="Could not fetch PR diff. Provide diff_text or check GitHub token.")

    if data.pr_number:
        pr_info = get_pr_info(data.repo_name, data.pr_number)

    review = Review(
        user_id=current_user.id,
        pr_number=data.pr_number,
        pr_title=pr_info.get("title", f"PR #{data.pr_number}") if pr_info else f"PR #{data.pr_number}",
        pr_author=pr_info.get("author", "unknown") if pr_info else "unknown",
        repo_name=data.repo_name,
        pr_url=pr_info.get("url", "") if pr_info else "",
        diff_text=diff_text,
        status="running",
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    background_tasks.add_task(
        run_review_background,
        db=db,
        review_id=review.id,
        diff_text=diff_text,
        pr_number=data.pr_number or 0,
        pr_title=review.pr_title,
        pr_author=review.pr_author,
        repo_name=data.repo_name,
        pr_url=review.pr_url,
    )

    return ReviewOut.model_validate(review)


@router.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """GitHub webhook endpoint — auto-triggered on PR events."""
    payload_bytes = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not verify_webhook_signature(payload_bytes, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()
    action = payload.get("action", "")
    pr_data = payload.get("pull_request", {})
    repo_data = payload.get("repository", {})

    if action not in ["opened", "synchronize", "reopened"]:
        return {"message": f"Action '{action}' ignored"}

    pr_number = pr_data.get("number")
    repo_name = repo_data.get("full_name", "")

    if not pr_number or not repo_name:
        return {"message": "Missing PR data"}

    # Find user by repo (basic matching)
    review = Review(
        user_id=1,
        pr_number=pr_number,
        pr_title=pr_data.get("title", f"PR #{pr_number}"),
        pr_author=pr_data.get("user", {}).get("login", "unknown"),
        repo_name=repo_name,
        pr_url=pr_data.get("html_url", ""),
        status="running",
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    diff_text = get_pr_diff(repo_name, pr_number) or ""

    background_tasks.add_task(
        run_review_background,
        db=db,
        review_id=review.id,
        diff_text=diff_text,
        pr_number=pr_number,
        pr_title=review.pr_title,
        pr_author=review.pr_author,
        repo_name=repo_name,
        pr_url=review.pr_url,
    )

    return {"message": "Review triggered", "review_id": review.id}


@router.get("/", response_model=List[ReviewOut])
def list_reviews(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reviews = (
        db.query(Review)
        .filter(Review.user_id == current_user.id)
        .order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [ReviewOut.model_validate(r) for r in reviews]


@router.get("/{review_id}", response_model=ReviewOut)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = db.query(Review).filter(Review.id == review_id, Review.user_id == current_user.id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return ReviewOut.model_validate(review)


@router.get("/{review_id}/comment")
def get_review_comment(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = db.query(Review).filter(Review.id == review_id, Review.user_id == current_user.id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    from app.services.agents.reporter_agent import format_github_comment
    comment = format_github_comment({
        "overall_score": review.overall_score or 0,
        "verdict": (review.reviewer_output or {}).get("verdict", "Approve with suggestions"),
        "summary": review.summary or "",
        "issues": review.issues or [],
        "security_issues": review.security_issues or [],
        "performance_issues": review.performance_issues or [],
        "suggestions": review.suggestions or [],
        "positive_aspects": (review.reviewer_output or {}).get("positive_aspects", []),
        "must_fix_before_merge": (review.reviewer_output or {}).get("must_fix_before_merge", []),
        "similar_issues": review.similar_issues or [],
        "repo_name": review.repo_name,
        "pr_number": review.pr_number,
    })
    return {"comment": comment, "format": "markdown"}
