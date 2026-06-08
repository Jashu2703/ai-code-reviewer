from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.repository import Repository
from app.schemas import RepoCreate, RepoOut
from app.services.github_service import setup_webhook
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=RepoOut, status_code=201)
def add_repository(
    data: RepoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Repository).filter(
        Repository.user_id == current_user.id,
        Repository.github_repo == data.github_repo,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Repository already added")

    repo = Repository(user_id=current_user.id, github_repo=data.github_repo)
    db.add(repo)
    db.commit()
    db.refresh(repo)

    # Setup webhook if token available
    if settings.GITHUB_TOKEN:
        callback_url = f"https://ai-code-reviewer.onrender.com/api/reviews/webhook"
        webhook_id = setup_webhook(data.github_repo, callback_url)
        if webhook_id:
            repo.webhook_id = webhook_id
            db.commit()

    return RepoOut.model_validate(repo)


@router.get("/", response_model=List[RepoOut])
def list_repositories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repos = db.query(Repository).filter(Repository.user_id == current_user.id).all()
    return [RepoOut.model_validate(r) for r in repos]


@router.delete("/{repo_id}")
def delete_repository(
    repo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = db.query(Repository).filter(
        Repository.id == repo_id,
        Repository.user_id == current_user.id,
    ).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    db.delete(repo)
    db.commit()
    return {"message": "Repository removed"}
