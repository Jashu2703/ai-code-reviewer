from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=True)

    # PR info
    pr_number = Column(Integer, nullable=True)
    pr_title = Column(String, nullable=True)
    pr_author = Column(String, nullable=True)
    repo_name = Column(String, nullable=True)
    pr_url = Column(String, nullable=True)

    # Code diff
    diff_text = Column(Text, nullable=True)
    files_changed = Column(JSON, default=list)
    lines_added = Column(Integer, default=0)
    lines_removed = Column(Integer, default=0)

    # Review results
    overall_score = Column(Float, nullable=True)  # 0-10
    severity = Column(String, default="low")  # low, medium, high, critical
    issues = Column(JSON, default=list)
    suggestions = Column(JSON, default=list)
    security_issues = Column(JSON, default=list)
    performance_issues = Column(JSON, default=list)
    summary = Column(Text, nullable=True)

    # Agent metadata
    analyzer_output = Column(JSON, nullable=True)
    reviewer_output = Column(JSON, nullable=True)
    similar_issues = Column(JSON, default=list)

    # MLflow tracking
    mlflow_run_id = Column(String, nullable=True)

    # Status
    status = Column(String, default="pending")  # pending, running, completed, failed
    posted_to_github = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="reviews")
    repository = relationship("Repository", back_populates="reviews")
