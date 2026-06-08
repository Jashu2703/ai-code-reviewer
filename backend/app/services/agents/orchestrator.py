from typing import Dict, Any, TypedDict, List, Optional
from loguru import logger
import time

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.warning("LangGraph not available. Using sequential fallback.")

from app.services.agents.analyzer_agent import run_analyzer_agent
from app.services.agents.reviewer_agent import run_reviewer_agent
from app.services.agents.reporter_agent import run_reporter_agent


class ReviewState(TypedDict):
    # Input
    diff_text: str
    pr_number: Optional[int]
    pr_title: Optional[str]
    pr_author: Optional[str]
    repo_name: Optional[str]
    pr_url: Optional[str]

    # Analyzer output
    parsed_diff: Optional[Dict]
    lines_added: int
    lines_removed: int
    files_changed: List[str]
    similar_issues: List[Dict]
    analyzer_output: Optional[Dict]
    issues: List[Dict]
    security_issues: List[Dict]
    performance_issues: List[Dict]
    overall_score: float
    severity: str

    # Reviewer output
    reviewer_output: Optional[Dict]
    summary: str
    suggestions: List[str]
    verdict: str
    positive_aspects: List[str]
    must_fix_before_merge: List[str]

    # Reporter output
    github_comment: str
    posted_to_github: int
    status: str


def build_review_graph():
    """Build the LangGraph multi-agent state machine."""
    if not LANGGRAPH_AVAILABLE:
        return None

    graph = StateGraph(ReviewState)

    # Add nodes (agents)
    graph.add_node("analyzer", run_analyzer_agent)
    graph.add_node("reviewer", run_reviewer_agent)
    graph.add_node("reporter", run_reporter_agent)

    # Define edges (flow)
    graph.set_entry_point("analyzer")
    graph.add_edge("analyzer", "reviewer")
    graph.add_edge("reviewer", "reporter")
    graph.add_edge("reporter", END)

    return graph.compile()


def run_review_pipeline(
    diff_text: str,
    pr_number: Optional[int] = None,
    pr_title: Optional[str] = "Code Review",
    pr_author: Optional[str] = "Unknown",
    repo_name: Optional[str] = None,
    pr_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main entry point for the AI code review pipeline.
    Uses LangGraph if available, falls back to sequential execution.
    """
    start_time = time.time()

    initial_state: ReviewState = {
        "diff_text": diff_text,
        "pr_number": pr_number,
        "pr_title": pr_title,
        "pr_author": pr_author,
        "repo_name": repo_name,
        "pr_url": pr_url,
        "parsed_diff": None,
        "lines_added": 0,
        "lines_removed": 0,
        "files_changed": [],
        "similar_issues": [],
        "analyzer_output": None,
        "issues": [],
        "security_issues": [],
        "performance_issues": [],
        "overall_score": 7.0,
        "severity": "low",
        "reviewer_output": None,
        "summary": "",
        "suggestions": [],
        "verdict": "Approve with suggestions",
        "positive_aspects": [],
        "must_fix_before_merge": [],
        "github_comment": "",
        "posted_to_github": 0,
        "status": "running",
    }

    try:
        graph = build_review_graph()

        if graph:
            logger.info("Running review pipeline via LangGraph...")
            final_state = graph.invoke(initial_state)
        else:
            logger.info("Running review pipeline sequentially...")
            state = initial_state.copy()
            state = run_analyzer_agent(state)
            state = run_reviewer_agent(state)
            state = run_reporter_agent(state)
            final_state = state

        elapsed = time.time() - start_time
        final_state["elapsed_seconds"] = elapsed
        logger.info(f"Review pipeline completed in {elapsed:.2f}s")
        return final_state

    except Exception as e:
        logger.error(f"Review pipeline failed: {e}")
        return {
            **initial_state,
            "status": "failed",
            "summary": f"Review pipeline failed: {str(e)}",
            "overall_score": 0.0,
        }
