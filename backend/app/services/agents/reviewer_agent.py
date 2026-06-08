from typing import Dict, Any
from loguru import logger
from app.services.llm_client import call_llm, safe_parse_json


def run_reviewer_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reviewer Agent — Second agent in LangGraph pipeline.
    Responsibilities:
    - Takes analyzer output as context
    - Generates comprehensive review summary
    - Produces actionable suggestions
    - RAG: uses similar past issues as context
    - Determines final verdict
    """
    logger.info("Reviewer agent starting...")

    diff_text = state.get("diff_text", "")
    pr_title = state.get("pr_title", "")
    pr_author = state.get("pr_author", "")
    issues = state.get("issues", [])
    security_issues = state.get("security_issues", [])
    performance_issues = state.get("performance_issues", [])
    overall_score = state.get("overall_score", 7.0)
    similar_issues = state.get("similar_issues", [])

    # Build RAG context from similar past issues
    rag_context = ""
    if similar_issues:
        rag_context = "\n\nRAG CONTEXT — Similar issues from past reviews:\n"
        for si in similar_issues[:3]:
            rag_context += f"• {si.get('message', '')} → {si.get('suggestion', '')}\n"

    # Format issues for prompt
    issues_text = ""
    if issues:
        issues_text += f"\nCODE QUALITY ISSUES ({len(issues)}):\n"
        for i in issues[:5]:
            issues_text += f"  - [{i.get('severity','').upper()}] {i.get('file','')} — {i.get('message','')}\n"

    if security_issues:
        issues_text += f"\nSECURITY ISSUES ({len(security_issues)}):\n"
        for i in security_issues[:3]:
            issues_text += f"  - [{i.get('severity','').upper()}] {i.get('file','')} — {i.get('message','')}\n"

    if performance_issues:
        issues_text += f"\nPERFORMANCE ISSUES ({len(performance_issues)}):\n"
        for i in performance_issues[:3]:
            issues_text += f"  - [{i.get('severity','').upper()}] {i.get('file','')} — {i.get('message','')}\n"

    prompt = f"""You are a senior engineering reviewer writing the final review for a Pull Request.

PR: {pr_title}
AUTHOR: {pr_author}
OVERALL SCORE: {overall_score}/10
{issues_text}
{rag_context}

CODE DIFF (first 2000 chars):
{diff_text[:2000]}

Write a comprehensive review and return ONLY valid JSON (no markdown):
{{
  "summary": "<3-4 sentence executive summary of the PR quality, key concerns, and overall verdict>",
  "suggestions": [
    "<specific actionable improvement suggestion>",
    "<specific actionable improvement suggestion>",
    "<specific actionable improvement suggestion>"
  ],
  "positive_aspects": [
    "<something done well in this PR>"
  ],
  "verdict": "Approve|Approve with suggestions|Request changes|Block",
  "verdict_reason": "<one sentence explaining the verdict>",
  "must_fix_before_merge": [
    "<critical issue that must be fixed>"
  ],
  "overall_score": {overall_score}
}}

Be direct, professional, and specific. Reference actual code where possible."""

    response = call_llm(
        prompt,
        system="You are a senior software engineer writing a professional code review. Return valid JSON only.",
        max_tokens=1500,
    )

    review = safe_parse_json(response)
    if not review:
        review = {
            "summary": f"Automated review completed. Found {len(issues)} code quality issues, {len(security_issues)} security issues, and {len(performance_issues)} performance issues.",
            "suggestions": ["Review all flagged issues before merging", "Add tests for new functionality"],
            "positive_aspects": ["Code changes are focused and scoped"],
            "verdict": "Approve with suggestions" if overall_score >= 6 else "Request changes",
            "verdict_reason": f"Score {overall_score}/10 with {len(issues + security_issues)} total issues found.",
            "must_fix_before_merge": [i.get("message", "") for i in security_issues[:2]],
            "overall_score": overall_score,
        }

    state["reviewer_output"] = review
    state["summary"] = review.get("summary", "")
    state["suggestions"] = review.get("suggestions", [])
    state["verdict"] = review.get("verdict", "Approve with suggestions")
    state["positive_aspects"] = review.get("positive_aspects", [])
    state["must_fix_before_merge"] = review.get("must_fix_before_merge", [])

    logger.info(f"Reviewer done: verdict={state['verdict']}")
    return state
