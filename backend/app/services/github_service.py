import hmac
import hashlib
from typing import Optional, Dict, Any
from loguru import logger
from app.core.config import settings


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook HMAC signature."""
    if not signature or not signature.startswith("sha256="):
        return False
    expected = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


def get_pr_diff(repo_name: str, pr_number: int) -> Optional[str]:
    """Fetch PR diff from GitHub API."""
    if not settings.GITHUB_TOKEN:
        logger.warning("No GitHub token configured")
        return _mock_diff()

    try:
        from github import Github
        g = Github(settings.GITHUB_TOKEN)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)

        diff_parts = []
        for file in pr.get_files():
            if file.patch:
                diff_parts.append(f"diff --git a/{file.filename} b/{file.filename}")
                diff_parts.append(file.patch)

        return "\n".join(diff_parts) if diff_parts else ""

    except Exception as e:
        logger.error(f"Failed to fetch PR diff: {e}")
        return None


def get_pr_info(repo_name: str, pr_number: int) -> Optional[Dict[str, Any]]:
    """Fetch PR metadata from GitHub."""
    if not settings.GITHUB_TOKEN:
        return {
            "title": f"PR #{pr_number}",
            "author": "unknown",
            "url": f"https://github.com/{repo_name}/pull/{pr_number}",
            "body": "",
        }

    try:
        from github import Github
        g = Github(settings.GITHUB_TOKEN)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)

        return {
            "title": pr.title,
            "author": pr.user.login,
            "url": pr.html_url,
            "body": pr.body or "",
            "base_branch": pr.base.ref,
            "head_branch": pr.head.ref,
        }

    except Exception as e:
        logger.error(f"Failed to fetch PR info: {e}")
        return None


def setup_webhook(repo_name: str, callback_url: str) -> Optional[int]:
    """Setup GitHub webhook for a repository."""
    if not settings.GITHUB_TOKEN:
        logger.warning("No GitHub token — cannot setup webhook")
        return None

    try:
        from github import Github
        g = Github(settings.GITHUB_TOKEN)
        repo = g.get_repo(repo_name)

        hook = repo.create_hook(
            name="web",
            config={
                "url": callback_url,
                "content_type": "json",
                "secret": settings.GITHUB_WEBHOOK_SECRET,
            },
            events=["pull_request"],
            active=True,
        )
        logger.info(f"Webhook created: {hook.id}")
        return hook.id

    except Exception as e:
        logger.error(f"Failed to create webhook: {e}")
        return None


def _mock_diff() -> str:
    """Mock diff for testing without GitHub token."""
    return """diff --git a/app/main.py b/app/main.py
index 1234567..abcdefg 100644
--- a/app/main.py
+++ b/app/main.py
@@ -1,10 +1,20 @@
+import os
 from fastapi import FastAPI
+from fastapi import HTTPException

 app = FastAPI()

+# TODO: move to env variable
+API_KEY = "hardcoded-secret-key-123"
+
 @app.get("/users")
-def get_users():
-    return []
+def get_users(skip: int = 0, limit: int = 100):
+    users = []
+    for i in range(1000000):
+        users.append({"id": i})
+    return users[skip:skip+limit]
+
+@app.post("/data")
+def process_data(data: dict):
+    query = f"SELECT * FROM users WHERE id = {data['id']}"
+    return {"query": query}
"""
