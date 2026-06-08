from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime


# Auth
class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str
    github_username: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    github_username: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# Repository
class RepoCreate(BaseModel):
    github_repo: str


class RepoOut(BaseModel):
    id: int
    github_repo: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Review
class ReviewRequest(BaseModel):
    repo_name: str
    pr_number: int
    diff_text: Optional[str] = None


class IssueItem(BaseModel):
    file: str
    line: Optional[int] = None
    severity: str
    type: str
    message: str
    suggestion: str


class ReviewOut(BaseModel):
    id: int
    pr_number: Optional[int]
    pr_title: Optional[str]
    pr_author: Optional[str]
    repo_name: Optional[str]
    pr_url: Optional[str]
    overall_score: Optional[float]
    severity: str
    issues: List[Any]
    suggestions: List[Any]
    security_issues: List[Any]
    performance_issues: List[Any]
    summary: Optional[str]
    status: str
    lines_added: int
    lines_removed: int
    created_at: datetime

    class Config:
        from_attributes = True


# Webhook
class GitHubWebhookPayload(BaseModel):
    action: Optional[str] = None
    number: Optional[int] = None
    pull_request: Optional[dict] = None
    repository: Optional[dict] = None
