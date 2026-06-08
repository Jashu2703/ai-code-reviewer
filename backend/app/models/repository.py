from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    github_repo = Column(String, nullable=False)  # e.g. "Jashu2703/joblens-ai"
    is_active = Column(Boolean, default=True)
    webhook_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="repositories")
    reviews = relationship("Review", back_populates="repository", cascade="all, delete-orphan")
