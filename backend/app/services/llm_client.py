import httpx
import json
import re
from typing import Any, Optional
from loguru import logger
from app.core.config import settings


def call_llm(prompt: str, system: Optional[str] = None, max_tokens: int = 2000) -> str:
    """Call OpenRouter API — free Llama 3.1 8B model."""
    if not settings.OPENROUTER_API_KEY:
        logger.warning("No OpenRouter API key. Using mock response.")
        return _mock_response(prompt)

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        with httpx.Client(timeout=60) as client:
            response = client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://ai-code-reviewer.onrender.com",
                    "X-Title": "AI Code Reviewer",
                },
                json={
                    "model": "meta-llama/llama-3.1-8b-instruct:free",
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.2,
                },
            )
            data = response.json()

            if "error" in data:
                logger.error(f"OpenRouter error: {data['error']}")
                return _mock_response(prompt)

            return data["choices"][0]["message"]["content"]

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return _mock_response(prompt)


def safe_parse_json(text: str) -> Any:
    """Parse JSON from LLM response safely."""
    text = text.strip()
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}|\[.*\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
    return None


def _mock_response(prompt: str) -> str:
    """Mock response when API key not configured."""
    if "analyze" in prompt.lower() or "diff" in prompt.lower():
        return json.dumps({
            "issues": [
                {
                    "file": "main.py",
                    "line": 42,
                    "severity": "medium",
                    "type": "code_quality",
                    "message": "Function is too long and does multiple things",
                    "suggestion": "Break into smaller single-responsibility functions"
                }
            ],
            "security_issues": [],
            "performance_issues": [
                {
                    "file": "main.py",
                    "line": 15,
                    "severity": "low",
                    "type": "performance",
                    "message": "Unnecessary list comprehension inside loop",
                    "suggestion": "Move outside loop or use generator"
                }
            ],
            "overall_score": 7.2,
            "severity": "medium"
        })
    elif "review" in prompt.lower() or "summary" in prompt.lower():
        return json.dumps({
            "summary": "The PR introduces functional changes with minor code quality issues. No critical security vulnerabilities detected. Consider refactoring long functions and adding error handling.",
            "suggestions": [
                "Add type hints to all function parameters",
                "Add docstrings to public functions",
                "Consider adding unit tests for new functionality"
            ],
            "overall_score": 7.2,
            "verdict": "Approve with suggestions"
        })
    return json.dumps({"result": "mock response - configure OPENROUTER_API_KEY"})
