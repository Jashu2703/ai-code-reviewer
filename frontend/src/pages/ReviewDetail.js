import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { reviewAPI } from "../services/api";

const SEV_BADGE = { critical: "badge-red", high: "badge-yellow", medium: "badge-blue", low: "badge-green" };

function IssueCard({ issue, index }) {
  const sev = issue.severity || "low";
  return (
    <div style={{ padding: "12px 14px", background: "var(--bg3)", borderRadius: 8,
      border: "1px solid var(--border)", marginBottom: 8,
      borderLeft: `3px solid ${sev === "critical" ? "#f85149" : sev === "high" ? "#d29922" : sev === "medium" ? "#388bfd" : "#3fb950"}` }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
        <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
          <span className={`badge ${SEV_BADGE[sev] || "badge-gray"}`}>{sev}</span>
          <span className="badge badge-gray">{issue.type || "issue"}</span>
          {issue.file && <code style={{ fontSize: 11, color: "var(--text2)", background: "var(--bg)", padding: "1px 6px", borderRadius: 4 }}>{issue.file}{issue.line ? `:${issue.line}` : ""}</code>}
        </div>
      </div>
      <div style={{ fontSize: 13, color: "var(--text)", marginBottom: 6 }}>{issue.message}</div>
      {issue.suggestion && (
        <div style={{ fontSize: 12, color: "var(--primary)", display: "flex", gap: 6 }}>
          <span>💡</span> {issue.suggestion}
        </div>
      )}
    </div>
  );
}

export default function ReviewDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [comment, setComment] = useState("");
  const [polling, setPolling] = useState(false);

  useEffect(() => {
    loadReview();
  }, [id]);

  const loadReview = async () => {
    try {
      const res = await reviewAPI.get(id);
      setReview(res.data);
      if (res.data.status === "running") {
        setPolling(true);
        setTimeout(loadReview, 3000);
      } else {
        setPolling(false);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const loadComment = async () => {
    try {
      const res = await reviewAPI.getComment(id);
      setComment(res.data.comment);
      setActiveTab("comment");
    } catch (e) { console.error(e); }
  };

  if (loading) return <div style={{ textAlign: "center", padding: "4rem", color: "var(--text2)" }}>Loading review...</div>;
  if (!review) return <div style={{ textAlign: "center", padding: "4rem", color: "var(--danger)" }}>Review not found</div>;

  const score = review.overall_score;
  const scoreColor = !score ? "var(--text2)" : score >= 8 ? "#3fb950" : score >= 6 ? "#d29922" : "#f85149";
  const allIssues = [...(review.issues || []), ...(review.security_issues || []), ...(review.performance_issues || [])];

  const TABS = [
    { id: "overview", label: "Overview" },
    { id: "issues", label: `Issues (${allIssues.length})` },
    { id: "security", label: `Security (${(review.security_issues || []).length})` },
    { id: "comment", label: "GitHub Comment" },
  ];

  return (
    <div>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
        <div>
          <button onClick={() => navigate("/reviews")} style={{ background: "none", border: "none", color: "var(--text2)", cursor: "pointer", fontSize: 13, marginBottom: 8 }}>
            ← Back to reviews
          </button>
          <h1 className="page-title">
            {review.repo_name} {review.pr_number ? `#${review.pr_number}` : ""}
          </h1>
          <p style={{ color: "var(--text2)", fontSize: 13 }}>{review.pr_title}</p>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          {polling && <><span className="spinner" /><span style={{ fontSize: 12, color: "var(--warning)" }}>Reviewing...</span></>}
          <span className={`badge badge-${review.status === "completed" ? "green" : review.status === "failed" ? "red" : "yellow"}`}>
            {review.status}
          </span>
        </div>
      </div>

      {/* Score cards */}
      {review.status === "completed" && (
        <div className="grid-4" style={{ marginBottom: 20 }}>
          <div className="card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: 32, fontWeight: 700, color: scoreColor }}>{score?.toFixed(1) || "—"}</div>
            <div style={{ fontSize: 12, color: "var(--text2)" }}>Overall Score</div>
          </div>
          <div className="card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: 32, fontWeight: 700, color: "#f85149" }}>{(review.security_issues || []).length}</div>
            <div style={{ fontSize: 12, color: "var(--text2)" }}>Security Issues</div>
          </div>
          <div className="card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: 32, fontWeight: 700, color: "#d29922" }}>{(review.issues || []).length}</div>
            <div style={{ fontSize: 12, color: "var(--text2)" }}>Code Issues</div>
          </div>
          <div className="card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: 32, fontWeight: 700, color: "var(--primary)" }}>+{review.lines_added || 0}/-{review.lines_removed || 0}</div>
            <div style={{ fontSize: 12, color: "var(--text2)" }}>Lines Changed</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: "flex", gap: 4, marginBottom: 16, borderBottom: "1px solid var(--border)", paddingBottom: 0 }}>
        {TABS.map(t => (
          <button key={t.id} onClick={() => { setActiveTab(t.id); if (t.id === "comment" && !comment) loadComment(); }}
            style={{ padding: "8px 16px", border: "none", background: "none", cursor: "pointer",
              fontSize: 13, fontWeight: 500, color: activeTab === t.id ? "var(--primary)" : "var(--text2)",
              borderBottom: activeTab === t.id ? "2px solid var(--primary)" : "2px solid transparent",
              marginBottom: -1 }}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Overview tab */}
      {activeTab === "overview" && (
        <div>
          {review.status === "running" && (
            <div className="card" style={{ textAlign: "center", padding: "3rem" }}>
              <div className="spinner" style={{ margin: "0 auto 12px", width: 32, height: 32, borderWidth: 3 }} />
              <p style={{ fontWeight: 500 }}>AI agents are reviewing your code...</p>
              <p style={{ fontSize: 13, color: "var(--text2)", marginTop: 4 }}>Analyzer → Reviewer → Reporter pipeline running</p>
            </div>
          )}
          {review.summary && (
            <div className="card" style={{ marginBottom: 16 }}>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 8 }}>📋 Review Summary</h3>
              <p style={{ fontSize: 14, color: "var(--text)", lineHeight: 1.7 }}>{review.summary}</p>
            </div>
          )}
          {review.suggestions?.length > 0 && (
            <div className="card" style={{ marginBottom: 16 }}>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 10 }}>💡 Suggestions</h3>
              {review.suggestions.map((s, i) => (
                <div key={i} style={{ fontSize: 13, color: "var(--text)", marginBottom: 6, display: "flex", gap: 8 }}>
                  <span style={{ color: "var(--primary)", flexShrink: 0 }}>{i + 1}.</span> {s}
                </div>
              ))}
            </div>
          )}
          {review.files_changed?.length > 0 && (
            <div className="card">
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 10 }}>📁 Files Changed</h3>
              {review.files_changed.map((f, i) => (
                <code key={i} style={{ display: "block", fontSize: 12, color: "var(--text2)", marginBottom: 4, padding: "2px 6px", background: "var(--bg3)", borderRadius: 4 }}>{f}</code>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Issues tab */}
      {activeTab === "issues" && (
        <div>
          {(review.performance_issues || []).length > 0 && (
            <div style={{ marginBottom: 16 }}>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 10, color: "var(--warning)" }}>⚡ Performance Issues</h3>
              {review.performance_issues.map((issue, i) => <IssueCard key={i} issue={issue} index={i} />)}
            </div>
          )}
          {(review.issues || []).length > 0 && (
            <div>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 10 }}>⚠️ Code Quality Issues</h3>
              {review.issues.map((issue, i) => <IssueCard key={i} issue={issue} index={i} />)}
            </div>
          )}
          {allIssues.length === 0 && (
            <div className="card" style={{ textAlign: "center", padding: "3rem" }}>
              <div style={{ fontSize: 32, marginBottom: 8 }}>✅</div>
              <p style={{ color: "var(--success)" }}>No code quality issues found</p>
            </div>
          )}
        </div>
      )}

      {/* Security tab */}
      {activeTab === "security" && (
        <div>
          {(review.security_issues || []).length > 0 ? (
            review.security_issues.map((issue, i) => <IssueCard key={i} issue={issue} index={i} />)
          ) : (
            <div className="card" style={{ textAlign: "center", padding: "3rem" }}>
              <div style={{ fontSize: 32, marginBottom: 8 }}>🔒</div>
              <p style={{ color: "var(--success)" }}>No security issues found</p>
            </div>
          )}
        </div>
      )}

      {/* GitHub comment tab */}
      {activeTab === "comment" && (
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <h3 style={{ fontSize: 14, fontWeight: 600 }}>GitHub PR Comment (Markdown)</h3>
            <button onClick={() => { navigator.clipboard.writeText(comment); }}
              className="btn btn-outline" style={{ fontSize: 12, padding: "4px 12px" }}>
              Copy
            </button>
          </div>
          {comment ? (
            <pre style={{ whiteSpace: "pre-wrap", fontSize: 12, color: "var(--text)", lineHeight: 1.6,
              background: "var(--bg3)", padding: 16, borderRadius: 8, fontFamily: "JetBrains Mono, monospace", overflow: "auto" }}>
              {comment}
            </pre>
          ) : (
            <div style={{ textAlign: "center", padding: "2rem", color: "var(--text2)" }}>Loading comment...</div>
          )}
        </div>
      )}
    </div>
  );
}
