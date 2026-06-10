# 🤖 AI Code Reviewer

> **Multi-agent AI system that automatically reviews GitHub Pull Requests** — detects bugs, security vulnerabilities, and performance issues, then posts structured feedback directly to your PR.

🔗 **Live Demo:** [ai-code-reviewer-nine9.vercel.app](https://ai-code-reviewer-nine9.vercel.app)  
📡 **API Docs:** [ai-code-reviewer.onrender.com/docs](https://ai-code-reviewer.onrender.com/docs)

---

## What It Does

Connect a GitHub repository, and every time a PR is opened or updated, the system:

1. **Fetches the PR diff** via GitHub API or webhook
2. **Runs a 3-agent LangGraph pipeline** — Analyzer → Reviewer → Reporter
3. **Posts a structured review comment** directly on the GitHub PR with scores, issues, and fix suggestions
4. **Learns over time** — stores past issues in FAISS so similar problems are surfaced in future reviews

---

## Architecture

```
GitHub PR Event (webhook / manual trigger)
        │
        ▼
┌─────────────────────────────────────────────┐
│           LangGraph State Machine            │
│                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌───────────────┐  │
│  │  Analyzer   │───▶│  Reviewer   │───▶│   Reporter    │  │
│  │   Agent     │    │   Agent     │    │    Agent      │  │
│  └─────────────┘    └─────────────┘    └───────────────┘  │
│   • Parse diff       • Summarize         • Format comment  │
│   • CodeBERT embed   • Verdict           • Post to GitHub  │
│   • FAISS search     • Suggestions       • Store in FAISS  │
│   • LLM analysis     • Positive aspects  • MLflow log      │
└─────────────────────────────────────────────┘
        │
        ▼
  GitHub PR Comment + MLflow Metrics Dashboard
```

**Stack:**
- **Backend:** FastAPI, Python, SQLAlchemy, PostgreSQL
- **AI Pipeline:** LangGraph, OpenRouter (Llama 3.1 8B), CodeBERT embeddings
- **Vector Store:** FAISS (persisted code issue index)
- **MLOps:** MLflow experiment tracking + LangSmith tracing
- **Auth:** JWT / bcrypt
- **GitHub:** PyGitHub — webhook handling, PR commenting
- **Frontend:** React (Vercel)
- **Infra:** Docker Compose (Postgres + Backend + MLflow + Frontend), Render

---

## Features

| Feature | Details |
|---|---|
| **Multi-agent review** | LangGraph 3-agent pipeline with typed state |
| **Code quality analysis** | Bugs, naming issues, maintainability, logic errors |
| **Security scanning** | SQL injection, hardcoded secrets, auth bypass, XSS |
| **Performance detection** | N+1 queries, memory leaks, blocking calls |
| **Overall score** | 0–10 score with severity classification |
| **GitHub auto-comment** | Formatted Markdown posted directly to PR |
| **RAG context** | Past issues retrieved from FAISS to improve review accuracy |
| **MLflow dashboard** | Per-review metrics: score, issue counts, latency, verdict |
| **LangSmith tracing** | Full LangChain trace for every pipeline run |
| **Webhook support** | Auto-triggered on PR open / update / reopen |
| **Manual trigger** | POST endpoint to review any PR on demand |

---

## Getting Started

### Prerequisites
- Docker and Docker Compose
- OpenRouter API key (free tier works) → [openrouter.ai](https://openrouter.ai)
- GitHub Personal Access Token (repo + webhook scopes)

### 1. Clone and configure

```bash
git clone https://github.com/Jashu2703/ai-code-reviewer.git
cd ai-code-reviewer
cp .env.example .env
```

Edit `.env`:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
GITHUB_TOKEN=your_github_pat
GITHUB_WEBHOOK_SECRET=any_random_string
SECRET_KEY=any_random_jwt_secret
LANGCHAIN_API_KEY=your_langsmith_key   # optional
DATABASE_URL=postgresql://reviewer:reviewer_secret@db:5432/code_reviewer_db
MLFLOW_TRACKING_URI=http://mlflow:5000
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

This starts 4 services:

| Service | Port | URL |
|---|---|---|
| FastAPI backend | 8000 | http://localhost:8000/docs |
| React frontend | 3000 | http://localhost:3000 |
| MLflow tracking | 5000 | http://localhost:5000 |
| PostgreSQL | 5432 | — |

### 3. Connect a repository

1. Register/login at `http://localhost:3000`
2. Add your GitHub repo (e.g. `username/my-repo`)
3. The system auto-creates a GitHub webhook for the repo
4. Open a PR — review is posted automatically

### Manual trigger (no webhook needed)

```bash
curl -X POST http://localhost:8000/api/reviews/trigger \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"repo_name": "username/repo", "pr_number": 42}'
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login, get JWT |
| POST | `/api/reviews/trigger` | Manually trigger a PR review |
| POST | `/api/reviews/webhook` | GitHub webhook receiver |
| GET | `/api/reviews/` | List all reviews |
| GET | `/api/reviews/{id}` | Get review details |
| GET | `/api/reviews/{id}/comment` | Get formatted GitHub comment |
| POST | `/api/repos/` | Add a repository |
| GET | `/api/repos/` | List connected repositories |
| GET | `/api/analytics/dashboard` | User dashboard metrics |
| GET | `/api/analytics/mlflow` | MLflow experiment metrics |
| GET | `/api/analytics/faiss` | FAISS vector store stats |

Full interactive docs at `/docs` (Swagger) or `/redoc`.

---

## Example PR Review Output

```
## 🤖 AI Code Review

🟡 Score: 6.8/10    ⚠️ Request changes

### 📋 Summary
PR introduces a new authentication endpoint but has a critical SQL injection
vulnerability and missing input validation. Logic is mostly sound.

### 🚫 Must Fix Before Merge
- ❌ Unsanitized user input passed directly to SQL query in auth.py

### 🔒 Security Issues (1)
- [CRITICAL] `auth.py` line 34 — Direct string interpolation in SQL query
  > 💡 Use parameterized queries: db.execute(query, {"email": email})

### ⚠️ Code Quality Issues (3)
- [MEDIUM] `auth.py` — Function login() exceeds 50 lines; violates SRP
  > 💡 Extract token generation and user lookup into separate functions
...
```

---

## Project Structure

```
ai-code-reviewer/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # FastAPI routes (auth, reviews, repos, analytics)
│   │   ├── core/              # Config, database, security/JWT
│   │   ├── models/            # SQLAlchemy models (User, Review, Repository)
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/
│   │       ├── agents/        # LangGraph agents (analyzer, reviewer, reporter)
│   │       ├── embeddings/    # CodeBERT + FAISS vector store
│   │       ├── llm_client.py  # OpenRouter API client
│   │       └── mlflow_tracker.py  # MLflow experiment logging
│   ├── tests/                 # pytest test suite (10 tests)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                  # React frontend
├── docker-compose.yml         # 4-service Docker setup
└── .env.example
```

---

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

10 tests covering: health check, auth (register/login/duplicate/invalid), protected routes, diff parser, LLM mock, and FAISS store.

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![LangGraph](https://img.shields.io/badge/LangGraph-0.1.5-purple)
![MLflow](https://img.shields.io/badge/MLflow-2.11-orange)
![FAISS](https://img.shields.io/badge/FAISS-1.8-red)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![React](https://img.shields.io/badge/React-Frontend-cyan)

---

## Built by

**Jashwanth Valasa** — AI/ML Engineer  
[LinkedIn](https://linkedin.com/in/jashwanth-valasa) · [GitHub](https://github.com/Jashu2703) · [Portfolio](https://joblens-ai-nine.vercel.app)
