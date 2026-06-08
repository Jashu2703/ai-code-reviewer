from typing import Dict, Any, List
from loguru import logger
from app.services.llm_client import call_llm, safe_parse_json
from app.services.embeddings.code_embedder import get_faiss_store, embed_code


def parse_diff(diff_text: str) -> Dict[str, Any]:
    """Parse git diff into structured format."""
    files = []
    current_file = None
    lines_added = 0
    lines_removed = 0
    current_chunks = []

    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            if current_file:
                files.append({
                    "filename": current_file,
                    "chunks": current_chunks,
                })
            current_file = line.split(" b/")[-1] if " b/" in line else line
            current_chunks = []
        elif line.startswith("+++") or line.startswith("---"):
            if line.startswith("+++") and line != "+++ /dev/null":
                current_file = line[4:].strip()
        elif line.startswith("+") and not line.startswith("+++"):
            lines_added += 1
            current_chunks.append({"type": "added", "content": line[1:]})
        elif line.startswith("-") and not line.startswith("---"):
            lines_removed += 1
            current_chunks.append({"type": "removed", "content": line[1:]})

    if current_file:
        files.append({"filename": current_file, "chunks": current_chunks})

    return {
        "files": files,
        "lines_added": lines_added,
        "lines_removed": lines_removed,
        "total_files": len(files),
    }


def run_analyzer_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzer Agent — First agent in LangGraph pipeline.
    Responsibilities:
    - Parse the PR diff
    - Generate code embeddings
    - Search for similar past issues in FAISS
    - Initial code analysis via LLM
    """
    logger.info("Analyzer agent starting...")
    diff_text = state.get("diff_text", "")
    pr_title = state.get("pr_title", "Unknown PR")

    # Parse diff
    parsed = parse_diff(diff_text)
    state["parsed_diff"] = parsed
    state["lines_added"] = parsed["lines_added"]
    state["lines_removed"] = parsed["lines_removed"]
    state["files_changed"] = [f["filename"] for f in parsed["files"]]

    # Search similar issues from FAISS
    faiss_store = get_faiss_store()
    similar_issues = []
    if diff_text:
        similar_issues = faiss_store.search_similar(diff_text[:1000], top_k=3)
    state["similar_issues"] = similar_issues

    # Build similar issues context
    similar_context = ""
    if similar_issues:
        similar_context = "\n\nSIMILAR PAST ISSUES FOUND:\n"
        for issue in similar_issues[:2]:
            similar_context += f"- {issue.get('message', '')} (score: {issue.get('similarity_score', 0):.2f})\n"

    # LLM analysis
    prompt = f"""You are an expert code reviewer analyzing a GitHub Pull Request.

PR TITLE: {pr_title}
FILES CHANGED: {', '.join(state['files_changed'][:10])}
LINES ADDED: {parsed['lines_added']} | LINES REMOVED: {parsed['lines_removed']}

CODE DIFF:
{diff_text[:3000]}
{similar_context}

Analyze this code change and return ONLY valid JSON (no markdown):
{{
  "issues": [
    {{
      "file": "<filename>",
      "line": <line_number_or_null>,
      "severity": "low|medium|high|critical",
      "type": "bug|code_quality|maintainability|naming|logic_error",
      "message": "<specific issue description>",
      "suggestion": "<specific fix suggestion>"
    }}
  ],
  "security_issues": [
    {{
      "file": "<filename>",
      "line": <line_number_or_null>,
      "severity": "medium|high|critical",
      "type": "sql_injection|xss|hardcoded_secret|insecure_dependency|auth_bypass",
      "message": "<security issue description>",
      "suggestion": "<specific security fix>"
    }}
  ],
  "performance_issues": [
    {{
      "file": "<filename>",
      "line": <line_number_or_null>,
      "severity": "low|medium|high",
      "type": "n_plus_one|memory_leak|inefficient_loop|blocking_call",
      "message": "<performance issue description>",
      "suggestion": "<specific optimization>"
    }}
  ],
  "overall_score": <float 0.0-10.0>,
  "severity": "low|medium|high|critical"
}}

Be specific. Reference actual code from the diff. Score 9+ only for excellent clean code."""

    response = call_llm(
        prompt,
        system="You are a senior software engineer doing thorough code review. Always return valid JSON only.",
        max_tokens=2000,
    )

    analysis = safe_parse_json(response)
    if not analysis:
        analysis = {
            "issues": [],
            "security_issues": [],
            "performance_issues": [],
            "overall_score": 7.0,
            "severity": "low",
        }

    state["analyzer_output"] = analysis
    state["issues"] = analysis.get("issues", [])
    state["security_issues"] = analysis.get("security_issues", [])
    state["performance_issues"] = analysis.get("performance_issues", [])
    state["overall_score"] = analysis.get("overall_score", 7.0)
    state["severity"] = analysis.get("severity", "low")

    logger.info(f"Analyzer done: {len(state['issues'])} issues, score={state['overall_score']}")
    return state
