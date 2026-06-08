import time
from typing import Dict, Any, Optional
from loguru import logger
from app.core.config import settings


def track_review(review_result: Dict[str, Any], review_id: int) -> Optional[str]:
    """
    Track code review metrics in MLflow.
    Records: score, severity, issue counts, latency, model used.
    """
    try:
        import mlflow
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        mlflow.set_experiment("ai-code-reviews")

        with mlflow.start_run(run_name=f"review_{review_id}") as run:
            # Log parameters
            mlflow.log_params({
                "repo_name": review_result.get("repo_name", "unknown"),
                "pr_number": review_result.get("pr_number", 0),
                "llm_model": "meta-llama/llama-3.1-8b-instruct:free",
                "embedding_model": "CodeBERT",
                "pipeline": "LangGraph 3-agent",
            })

            # Log metrics
            mlflow.log_metrics({
                "overall_score": float(review_result.get("overall_score", 0)),
                "issues_count": len(review_result.get("issues", [])),
                "security_issues_count": len(review_result.get("security_issues", [])),
                "performance_issues_count": len(review_result.get("performance_issues", [])),
                "lines_added": float(review_result.get("lines_added", 0)),
                "lines_removed": float(review_result.get("lines_removed", 0)),
                "files_changed": float(len(review_result.get("files_changed", []))),
                "similar_issues_found": float(len(review_result.get("similar_issues", []))),
                "elapsed_seconds": float(review_result.get("elapsed_seconds", 0)),
                "posted_to_github": float(review_result.get("posted_to_github", 0)),
            })

            # Log artifacts
            summary = review_result.get("summary", "")
            if summary:
                mlflow.log_text(summary, "review_summary.txt")

            github_comment = review_result.get("github_comment", "")
            if github_comment:
                mlflow.log_text(github_comment, "github_comment.md")

            # Log tags
            mlflow.set_tags({
                "severity": review_result.get("severity", "low"),
                "verdict": review_result.get("verdict", "unknown"),
                "status": review_result.get("status", "unknown"),
            })

            run_id = run.info.run_id
            logger.info(f"MLflow run logged: {run_id}")
            return run_id

    except Exception as e:
        logger.warning(f"MLflow tracking failed (non-critical): {e}")
        return None


def get_review_metrics() -> Dict[str, Any]:
    """Get aggregated metrics from MLflow for dashboard."""
    try:
        import mlflow
        from mlflow.tracking import MlflowClient

        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        client = MlflowClient()

        experiment = client.get_experiment_by_name("ai-code-reviews")
        if not experiment:
            return {"total_reviews": 0, "avg_score": 0, "runs": []}

        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            max_results=50,
            order_by=["start_time DESC"],
        )

        if not runs:
            return {"total_reviews": 0, "avg_score": 0, "runs": []}

        scores = [r.data.metrics.get("overall_score", 0) for r in runs]
        avg_score = sum(scores) / len(scores) if scores else 0

        return {
            "total_reviews": len(runs),
            "avg_score": round(avg_score, 2),
            "total_issues": sum(r.data.metrics.get("issues_count", 0) for r in runs),
            "total_security_issues": sum(r.data.metrics.get("security_issues_count", 0) for r in runs),
            "runs": [
                {
                    "run_id": r.info.run_id,
                    "score": r.data.metrics.get("overall_score", 0),
                    "severity": r.data.tags.get("severity", "low"),
                    "verdict": r.data.tags.get("verdict", ""),
                    "repo": r.data.params.get("repo_name", ""),
                    "pr_number": r.data.params.get("pr_number", ""),
                    "start_time": r.info.start_time,
                }
                for r in runs[:20]
            ],
        }
    except Exception as e:
        logger.warning(f"Could not fetch MLflow metrics: {e}")
        return {"total_reviews": 0, "avg_score": 0, "runs": [], "error": str(e)}
