import React, { useState, useEffect } from "react";
import { analyticsAPI } from "../services/api";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, CartesianGrid } from "recharts";

export default function Analytics() {
  const [dashboard, setDashboard] = useState(null);
  const [mlflow, setMlflow] = useState(null);
  const [faiss, setFaiss] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      analyticsAPI.dashboard(),
      analyticsAPI.mlflow(),
      analyticsAPI.faiss(),
    ]).then(([d, m, f]) => {
      setDashboard(d.data);
      setMlflow(m.data);
      setFaiss(f.data);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ textAlign: "center", padding: "4rem", color: "var(--text2)" }}>Loading analytics...</div>;

  const chartData = (mlflow?.runs || []).slice(0, 10).reverse().map((r, i) => ({
    name: `PR #${r.pr_number || i + 1}`,
    score: parseFloat(r.score?.toFixed(1) || 0),
  }));

  const stats = [
    { label: "Total Reviews", value: dashboard?.total_reviews || 0, color: "var(--primary)" },
    { label: "Avg Score (MLflow)", value: mlflow?.avg_score ? `${mlflow.avg_score}/10` : "—", color: "#3fb950" },
    { label: "Total Issues Tracked", value: mlflow?.total_issues || 0, color: "#d29922" },
    { label: "Security Issues", value: mlflow?.total_security_issues || 0, color: "#f85149" },
    { label: "FAISS Vectors", value: faiss?.total_vectors || 0, color: "var(--purple)" },
    { label: "Completed Reviews", value: dashboard?.completed_reviews || 0, color: "#3fb950" },
  ];

  return (
    <div>
      <h1 className="page-title">Analytics & MLOps Dashboard</h1>
      <p className="page-sub">MLflow experiment tracking · LangSmith traces · FAISS vector stats</p>

      <div className="grid-3" style={{ marginBottom: 24 }}>
        {stats.map(s => (
          <div key={s.label} className="card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: 26, fontWeight: 700, color: s.color }}>{s.value}</div>
            <div style={{ fontSize: 12, color: "var(--text2)", marginTop: 4 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {chartData.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16 }}>📊 Review Scores Over Time (MLflow)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: "var(--text2)" }} />
              <YAxis domain={[0, 10]} tick={{ fontSize: 11, fill: "var(--text2)" }} />
              <Tooltip contentStyle={{ background: "var(--bg2)", border: "1px solid var(--border)", borderRadius: 8 }} />
              <Line type="monotone" dataKey="score" stroke="var(--primary)" strokeWidth={2} dot={{ fill: "var(--primary)" }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="grid-2">
        <div className="card">
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>🔍 FAISS Vector Store</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
              <span style={{ color: "var(--text2)" }}>Total vectors indexed</span>
              <span style={{ color: "var(--purple)", fontWeight: 600 }}>{faiss?.total_vectors || 0}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
              <span style={{ color: "var(--text2)" }}>Embedding model</span>
              <span style={{ color: "var(--text)" }}>CodeBERT</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
              <span style={{ color: "var(--text2)" }}>Vector dimensions</span>
              <span style={{ color: "var(--text)" }}>768</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
              <span style={{ color: "var(--text2)" }}>Index type</span>
              <span style={{ color: "var(--text)" }}>FAISS FlatL2</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
              <span style={{ color: "var(--text2)" }}>Use case</span>
              <span style={{ color: "var(--text)" }}>Semantic issue search</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>🧪 MLflow Experiment</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
              <span style={{ color: "var(--text2)" }}>Experiment name</span>
              <code style={{ fontSize: 11, color: "var(--primary)", background: "var(--bg3)", padding: "1px 6px", borderRadius: 4 }}>ai-code-reviews</code>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
              <span style={{ color: "var(--text2)" }}>Total runs</span>
              <span style={{ color: "var(--text)", fontWeight: 600 }}>{mlflow?.total_reviews || 0}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
              <span style={{ color: "var(--text2)" }}>Avg score</span>
              <span style={{ color: "#3fb950", fontWeight: 600 }}>{mlflow?.avg_score || "—"}/10</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
              <span style={{ color: "var(--text2)" }}>Tracked metrics</span>
              <span style={{ color: "var(--text)" }}>score, latency, issues</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
              <span style={{ color: "var(--text2)" }}>LLM pipeline</span>
              <span style={{ color: "var(--text)" }}>LangGraph 3-agent</span>
            </div>
          </div>
        </div>
      </div>

      {mlflow?.runs?.length > 0 && (
        <div className="card" style={{ marginTop: 20 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>📋 MLflow Run History</h3>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)" }}>
                  {["Run ID", "Repo", "PR", "Score", "Severity", "Verdict"].map(h => (
                    <th key={h} style={{ padding: "8px 12px", textAlign: "left", color: "var(--text2)", fontWeight: 500, fontSize: 12 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {mlflow.runs.slice(0, 10).map(r => (
                  <tr key={r.run_id} style={{ borderBottom: "1px solid var(--border)" }}>
                    <td style={{ padding: "8px 12px" }}><code style={{ fontSize: 11, color: "var(--text2)" }}>{r.run_id?.slice(0, 8)}...</code></td>
                    <td style={{ padding: "8px 12px", color: "var(--text2)" }}>{r.repo || "—"}</td>
                    <td style={{ padding: "8px 12px", color: "var(--text2)" }}>#{r.pr_number || "—"}</td>
                    <td style={{ padding: "8px 12px", fontWeight: 600, color: r.score >= 8 ? "#3fb950" : r.score >= 6 ? "#d29922" : "#f85149" }}>{r.score?.toFixed(1)}</td>
                    <td style={{ padding: "8px 12px" }}><span className={`badge badge-${r.severity === "critical" ? "red" : r.severity === "high" ? "yellow" : r.severity === "medium" ? "blue" : "green"}`}>{r.severity}</span></td>
                    <td style={{ padding: "8px 12px", color: "var(--text2)", fontSize: 12 }}>{r.verdict}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
