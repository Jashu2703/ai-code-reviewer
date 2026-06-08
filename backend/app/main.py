from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from loguru import logger

from app.core.database import engine, Base
from app.api.routes import auth, reviews, analytics, repositories
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Code Reviewer...")
    Base.metadata.create_all(bind=engine)
    os.makedirs(settings.FAISS_INDEX_PATH, exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    logger.info("Database tables created. Server ready.")
    yield
    logger.info("Shutting down AI Code Reviewer.")


app = FastAPI(
    title="AI Code Reviewer",
    description="Multi-agent AI code review system using LangGraph + CodeBERT + MLflow",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(repositories.router, prefix="/api/repos", tags=["Repositories"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])


@app.get("/", tags=["Health"])
def root():
    return {
        "app": "AI Code Reviewer",
        "version": "1.0.0",
        "status": "running",
        "stack": ["LangGraph", "CodeBERT", "FAISS", "MLflow", "LangSmith", "OpenRouter", "FastAPI"],
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
