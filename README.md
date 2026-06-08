# 🤖 AI Code Reviewer

> Multi-agent AI code review system — LangGraph · CodeBERT · FAISS · MLflow · LangSmith · OpenRouter · FastAPI · React

---

## What it does

Automatically reviews GitHub Pull Requests using a 3-agent LangGraph pipeline:

1. **Analyzer Agent** — Parses diff, generates CodeBERT embeddings, searches FAISS for similar past issues
2. **Reviewer Agent** — LLM review with RAG context from codebase history
3. **Reporter Agent** — Posts formatted review comment to GitHub PR, stores issues in FAISS

Every review is tracked in **MLflow** with score, latency, issue counts, and LLM traces in **LangSmith**.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Multi-agent orchestration | LangGraph |
| LLM | OpenRouter (Llama 3.1 8B - free) |
| Code embeddings | CodeBERT (HuggingFace Transformers) |
| Vector search | FAISS (semantic issue retrieval) |
| RAG pipeline | LangChain |
| MLOps tracking | MLflow |
| LLMOps tracing | LangSmith |
| Backend | FastAPI + Python 3.11 |
| Database | PostgreSQL |
| Frontend | React 18 |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Deployment | Render (free) + Vercel (free) |

---

## Quick Start

### 1. Get free API keys
- **OpenRouter**: https://openrouter.ai (free tier)
- **LangSmith**: https://smith.langchain.com (free tier)
- **GitHub Token**: https://github.com/settings/tokens → repo scope

### 2. Clone and configure
```bash
git clone https://github.com/YOUR_USERNAME/ai-code-reviewer.git
cd ai-code-reviewer
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run with Docker
```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- MLflow UI: http://localhost:5000

### 4. Without Docker (local dev)
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Run PostgreSQL separately or use SQLite for dev
uvicorn app.main:app --reload --port 8000
```

---

## Usage

### Trigger a review manually
```bash
curl -X POST http://localhost:8000/api/reviews/trigger \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"repo_name": "owner/repo", "pr_number": 42}'
```

### Setup GitHub webhook (auto-review on every PR)
```
Webhook URL: https://your-backend.onrender.com/api/reviews/webhook
Content type: application/json
Secret: your GITHUB_WEBHOOK_SECRET value
Events: Pull requests
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login |
| POST | `/api/reviews/trigger` | Manual review trigger |
| POST | `/api/reviews/webhook` | GitHub webhook |
| GET | `/api/reviews/` | List all reviews |
| GET | `/api/reviews/{id}` | Get review details |
| GET | `/api/reviews/{id}/comment` | Get GitHub comment markdown |
| GET | `/api/analytics/dashboard` | Dashboard metrics |
| GET | `/api/analytics/mlflow` | MLflow experiment data |
| GET | `/api/analytics/faiss` | FAISS vector store stats |

---

## Deploy to Render (free)

### Backend
1. Go to render.com → New Web Service
2. Connect GitHub repo
3. Root directory: `backend`
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables from `.env`

### Frontend
1. Go to vercel.com → New Project
2. Connect GitHub repo
3. Root directory: `frontend`
4. Add: `REACT_APP_API_URL=https://your-backend.onrender.com`

---

## Resume Bullet

> Built and deployed **AI Code Reviewer** — multi-agent code review system using LangGraph (3-agent pipeline: Analyzer → Reviewer → Reporter), CodeBERT embeddings, FAISS semantic search, MLflow experiment tracking, LangSmith LLM tracing, GitHub webhook integration, CI/CD via GitHub Actions. Stack: FastAPI · React · PostgreSQL · Docker · Render.

---

## Project Structure

```
ai-code-reviewer/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # auth, reviews, analytics, repos
│   │   ├── core/              # config, database, security
│   │   ├── models/            # SQLAlchemy ORM
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/
│   │       ├── agents/        # analyzer, reviewer, reporter, orchestrator
│   │       ├── embeddings/    # CodeBERT + FAISS
│   │       ├── llm_client.py  # OpenRouter
│   │       ├── github_service.py
│   │       └── mlflow_tracker.py
│   └── tests/
├── frontend/src/
│   ├── pages/                 # Dashboard, Reviews, Analytics, NewReview
│   └── components/            # Navbar
├── .github/workflows/         # CI/CD pipeline
├── docker-compose.yml
└── render.yaml
```
