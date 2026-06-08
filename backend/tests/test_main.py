import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# Test database
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_root(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "AI Code Reviewer" in res.json()["app"]


def test_register(client):
    res = client.post("/api/auth/register", json={
        "name": "Test User",
        "email": "test@test.com",
        "password": "test1234",
    })
    assert res.status_code == 201
    assert "access_token" in res.json()


def test_login(client):
    # Register first
    client.post("/api/auth/register", json={
        "name": "Test User",
        "email": "login@test.com",
        "password": "test1234",
    })
    # Login
    res = client.post("/api/auth/login", json={
        "email": "login@test.com",
        "password": "test1234",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_duplicate_register(client):
    data = {"name": "Test", "email": "dup@test.com", "password": "test1234"}
    client.post("/api/auth/register", json=data)
    res = client.post("/api/auth/register", json=data)
    assert res.status_code == 400


def test_invalid_login(client):
    res = client.post("/api/auth/login", json={
        "email": "none@test.com",
        "password": "wrong",
    })
    assert res.status_code == 401


def test_reviews_requires_auth(client):
    res = client.get("/api/reviews/")
    assert res.status_code == 401


def test_diff_parser():
    from app.services.agents.analyzer_agent import parse_diff
    diff = """diff --git a/test.py b/test.py
+++ b/test.py
+def hello():
+    pass
-def old():
-    pass"""
    result = parse_diff(diff)
    assert "files" in result
    assert result["lines_added"] >= 0
    assert result["lines_removed"] >= 0


def test_llm_mock():
    from app.services.llm_client import call_llm
    # Without API key, should return mock
    result = call_llm("analyze this diff")
    assert result is not None
    assert len(result) > 0


def test_faiss_store():
    from app.services.embeddings.code_embedder import FAISSCodeStore
    store = FAISSCodeStore(index_path="./test_faiss")
    store.add_code_snippet("def hello(): pass", {"message": "test", "severity": "low"})
    results = store.search_similar("def hello(): pass", top_k=1)
    assert isinstance(results, list)

    # Cleanup
    import shutil
    shutil.rmtree("./test_faiss", ignore_errors=True)
