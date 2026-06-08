from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.review import Review
from app.services.mlflow_tracker import get_review_metrics
from app.services.embeddings.code_embedder import get_faiss_store

router = APIRouter()


@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get dashboard metrics for the current user."""
    total = db.query(Review).filter(Review.user_id == current_user.id).count()
    completed = db.query(Review).filter(Review.user_id == current_user.id, Review.status == "completed").count()
    failed = db.query(Review).filter(Review.user_id == current_user.id, Review.status == "failed").count()

    avg_score = db.query(func.avg(Review.overall_score)).filter(
        Review.user_id == current_user.id,
        Review.overall_score.isnot(None)
    ).scalar() or 0

    critical = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.severity == "critical"
    ).count()

    high = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.severity == "high"
    ).count()

    recent = (
        db.query(Review)
        .filter(Review.user_id == current_user.id)
        .order_by(Review.created_at.desc())
        .limit(5)
        .all()
    )

    faiss_stats = get_faiss_store().get_stats()

    return {
        "total_reviews": total,
        "completed_reviews": completed,
        "failed_reviews": failed,
        "avg_score": round(float(avg_score), 2),
        "critical_severity": critical,
        "high_severity": high,
        "faiss_vectors": faiss_stats.get("total_vectors", 0),
        "recent_reviews": [
            {
                "id": r.id,
                "repo_name": r.repo_name,
                "pr_number": r.pr_number,
                "pr_title": r.pr_title,
                "overall_score": r.overall_score,
                "severity": r.severity,
                "status": r.status,
                "created_at": r.created_at,
            }
            for r in recent
        ],
    }


@router.get("/mlflow")
def get_mlflow_metrics(current_user: User = Depends(get_current_user)):
    """Get MLflow experiment metrics."""
    return get_review_metrics()


@router.get("/faiss")
def get_faiss_stats(current_user: User = Depends(get_current_user)):
    """Get FAISS vector store statistics."""
    store = get_faiss_store()
    return store.get_stats()
