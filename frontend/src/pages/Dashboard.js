import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { analyticsAPI } from "../services/api";
import { useAuth } from "../App";

const SEV_COLOR = { critical: "#f85149", high: "#d29922", medium: "#388bfd", low: "#3fb950" };
const SEV_BG = { critical: "rgba(248,81,73,0.1)", high: "rgba(210,153,34,0.1)", medium: "rgba(56,139,253,0.1)", low: "rgba(63,185,80,0.1)" };

function ScoreBadge({ score }) {
  if (!score && score !== 0) return <span style={{ color: "var(--text3)" }}>—</span>;
  const color = score >= 8 ? "#3fb950" : score >= 6 ? "#d29922" : "#f85149";
  return <span style={{ color, fontWeight: 600 }}>{score.toFixed(1)}</span>;
}

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsAPI.dashboard()
      .then(r => setData(r.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const stats = [
    { label: "Total Reviews", value: data?.total_reviews || 0, color: "var(--primary)" },
    { label: "Avg Score", value: data?.avg_score ? `${data.avg_score}/10` : "—", color: "#3fb950" },
    { label: "Critical Issues", value: data?.critical_severity || 0, color: "#f85149" },
    { label: "FAISS Vectors", value: data?.faiss_vectors || 0, color: "var(--purple)" },
  ];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <h1 className="page-title">Welcome, {user?.name?.split(" ")[0]} 👋</h1>
          <p className="page-sub">AI-powered multi-agent code review dashboard</p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate("/new-review")}>
          + New Review
        </button>
      </div>

      {/* Stats */}
      <div className="grid-4" style={{ marginBottom: 24 }}>
        {stats.map(s => (
          <div key={s.label} className="card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: 28, fontWeight: 700, color: s.color }}>{loading ? "..." : s.value}</div>
            <div style={{ fontSize: 12, color: "var(--text2)", marginTop: 4 }}>{s.label}</div>
          </div>
        ))}
      </div>

      <div className="grid-2">
        {/* Recent Reviews */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <h2 style={{ fontSize: 15, fontWeight: 600 }}>Recent Reviews</h2>
            <Link to="/reviews" style={{ fontSize: 12, color: "var(--primary)", textDecoration: "none" }}>View all →</Link>
          </div>
          {loading ? (
            <div style={{ textAlign: "center", padding: "2rem", color: "var(--text2)" }}>Loading...</div>
          ) : !data?.recent_reviews?.length ? (
            <div style={{ textAlign: "center", padding: "2rem" }}>
              <div style={{ fontSize: 32, marginBottom: 8 }}>🤖</div>
              <p style={{ color: "var(--text2)", fontSize: 13, marginBottom: 12 }}>No reviews yet</p>
              <button className="btn btn-primary" onClick={() => navigate("/new-review")}>Run First Review</button>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {data.recent_reviews.map(r => (
                <Link key={r.id} to={`/reviews/${r.id}`} style={{ textDecoration: "none" }}>
                  <div style={{ padding: "10px 12px", background: "var(--bg3)", borderRadius: 8,
                    border: "1px solid var(--border)", cursor: "pointer" }}
                    onMouseEnter={e => e.currentTarget.style.borderColor = "var(--primary)"}
                    onMouseLeave={e => e.currentTarget.style.borderColor = "var(--border)"}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text)" }}>
                        {r.repo_name} #{r.pr_number}
                      </div>
                      <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                        <ScoreBadge score={r.overall_score} />
                        <span className={`badge badge-${r.status === "completed" ? "green" : r.status === "failed" ? "red" : "yellow"}`}>
                          {r.status}
                        </span>
                      </div>
                    </div>
                    {r.pr_title && (
                      <div style={{ fontSize: 12, color: "var(--text2)", marginTop: 2 }}>{r.pr_title}</div>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Quick Start */}
        <div className="card">
          <h2 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>How It Works</h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {[
              { step: "1", title: "Submit PR diff", desc: "Paste a GitHub PR URL or raw diff code", icon: "📋" },
              { step: "2", title: "Analyzer Agent", desc: "CodeBERT embeds code, FAISS finds similar past issues", icon: "🔍" },
              { step: "3", title: "Reviewer Agent", desc: "LLM reviews with RAG context from codebase history", icon: "🤖" },
              { step: "4", title: "Reporter Agent", desc: "Posts formatted review to GitHub PR automatically", icon: "📝" },
              { step: "5", title: "MLflow tracks", desc: "Every review logged: score, latency, issue count", icon: "📊" },
            ].map(item => (
              <div key={item.step} style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
                <div style={{ width: 32, height: 32, background: "rgba(56,139,253,0.1)", border: "1px solid rgba(56,139,253,0.2)",
                  borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 14, flexShrink: 0 }}>
                  {item.icon}
                </div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text)" }}>{item.title}</div>
                  <div style={{ fontSize: 12, color: "var(--text2)" }}>{item.desc}</div>
                </div>
              </div>
            ))}
          </div>
          <button className="btn btn-primary" onClick={() => navigate("/new-review")} style={{ marginTop: 16, width: "100%", justifyContent: "center" }}>
            Start a Review →
          </button>
        </div>
      </div>
    </div>
  );
}
