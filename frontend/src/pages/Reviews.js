import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { reviewAPI } from "../services/api";

const SEV_COLOR = { critical: "#f85149", high: "#d29922", medium: "#388bfd", low: "#3fb950" };

export default function Reviews() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    reviewAPI.list().then(r => setReviews(r.data)).catch(console.error).finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 className="page-title">All Reviews</h1>
          <p className="page-sub">{reviews.length} total reviews</p>
        </div>
        <Link to="/new-review" className="btn btn-primary">+ New Review</Link>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "4rem", color: "var(--text2)" }}>Loading...</div>
      ) : reviews.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "4rem" }}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>🤖</div>
          <h2 style={{ marginBottom: 8 }}>No reviews yet</h2>
          <p style={{ color: "var(--text2)", marginBottom: 16 }}>Run your first AI code review</p>
          <Link to="/new-review" className="btn btn-primary">Start Review</Link>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {reviews.map(r => (
            <Link key={r.id} to={`/reviews/${r.id}`} style={{ textDecoration: "none" }}>
              <div className="card" style={{ cursor: "pointer", transition: "border-color 0.15s" }}
                onMouseEnter={e => e.currentTarget.style.borderColor = "var(--primary)"}
                onMouseLeave={e => e.currentTarget.style.borderColor = "var(--border)"}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 4 }}>
                      <span style={{ fontWeight: 600, fontSize: 14 }}>{r.repo_name || "—"}</span>
                      {r.pr_number && <span style={{ color: "var(--text2)", fontSize: 13 }}>#{r.pr_number}</span>}
                      <span className={`badge badge-${r.status === "completed" ? "green" : r.status === "failed" ? "red" : "yellow"}`}>
                        {r.status}
                      </span>
                    </div>
                    {r.pr_title && <div style={{ fontSize: 13, color: "var(--text2)", marginBottom: 4 }}>{r.pr_title}</div>}
                    <div style={{ fontSize: 12, color: "var(--text3)" }}>
                      +{r.lines_added || 0} -{r.lines_removed || 0} lines · {new Date(r.created_at).toLocaleString()}
                    </div>
                  </div>
                  <div style={{ textAlign: "right", flexShrink: 0, marginLeft: 16 }}>
                    {r.overall_score != null && (
                      <div style={{ fontSize: 22, fontWeight: 700,
                        color: r.overall_score >= 8 ? "#3fb950" : r.overall_score >= 6 ? "#d29922" : "#f85149" }}>
                        {r.overall_score.toFixed(1)}
                      </div>
                    )}
                    {r.severity && (
                      <span style={{ fontSize: 11, color: SEV_COLOR[r.severity] || "var(--text2)" }}>
                        {r.severity}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
