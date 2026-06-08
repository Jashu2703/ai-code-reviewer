import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { reviewAPI } from "../services/api";

const SAMPLE_DIFF = `diff --git a/app/main.py b/app/main.py
index 1234567..abcdefg 100644
--- a/app/main.py
+++ b/app/main.py
@@ -1,8 +1,18 @@
+import os
 from fastapi import FastAPI
 
 app = FastAPI()
 
+# Hardcoded secret - should use env variable
+API_KEY = "sk-prod-hardcoded-key-12345"
+
 @app.get("/users")
-def get_users():
-    return []
+def get_users(skip: int = 0):
+    users = []
+    for i in range(1000000):
+        users.append({"id": i, "name": f"user_{i}"})
+    return users[skip:skip+10]
+
+@app.post("/query")  
+def run_query(data: dict):
+    sql = f"SELECT * FROM users WHERE name = '{data['name']}'"
+    return {"sql": sql}`;

export default function NewReview() {
  const navigate = useNavigate();
  const [mode, setMode] = useState("diff"); // diff | pr
  const [form, setForm] = useState({ repo_name: "", pr_number: "", diff_text: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async () => {
    if (mode === "diff" && !form.diff_text) { setError("Please paste a diff or use sample diff"); return; }
    if (mode === "pr" && (!form.repo_name || !form.pr_number)) { setError("Provide repo name and PR number"); return; }
    setLoading(true); setError("");
    try {
      const payload = {
        repo_name: form.repo_name || "demo/repository",
        pr_number: parseInt(form.pr_number) || 1,
        diff_text: mode === "diff" ? form.diff_text : null,
      };
      const res = await reviewAPI.trigger(payload);
      navigate(`/reviews/${res.data.id}`);
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to trigger review");
    } finally { setLoading(false); }
  };

  return (
    <div style={{ maxWidth: 800, margin: "0 auto" }}>
      <h1 className="page-title">New Code Review</h1>
      <p className="page-sub">Submit a PR diff or GitHub PR for AI-powered multi-agent review</p>

      {/* Mode selector */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        {[
          { id: "diff", label: "📋 Paste Diff" },
          { id: "pr", label: "🔗 GitHub PR" },
        ].map(m => (
          <button key={m.id} onClick={() => setMode(m.id)} style={{
            padding: "8px 16px", borderRadius: 6, border: "1px solid",
            borderColor: mode === m.id ? "var(--primary)" : "var(--border)",
            background: mode === m.id ? "rgba(56,139,253,0.1)" : "var(--bg2)",
            color: mode === m.id ? "var(--primary)" : "var(--text2)",
            cursor: "pointer", fontSize: 13, fontWeight: 500,
          }}>{m.label}</button>
        ))}
      </div>

      <div className="card">
        {mode === "diff" && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <label className="label">Repository Name <span style={{ color: "var(--text3)" }}>(optional)</span></label>
              <input className="input" placeholder="e.g. Jashu2703/joblens-ai"
                value={form.repo_name} onChange={e => setForm({ ...form, repo_name: e.target.value })} />
            </div>
            <div style={{ marginBottom: 8 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                <label className="label" style={{ margin: 0 }}>Git Diff</label>
                <button onClick={() => setForm({ ...form, diff_text: SAMPLE_DIFF })}
                  style={{ background: "none", border: "1px solid var(--border)", color: "var(--text2)",
                    padding: "3px 10px", borderRadius: 5, fontSize: 11, cursor: "pointer" }}>
                  Load sample diff
                </button>
              </div>
              <textarea className="textarea" placeholder="Paste your git diff here..." style={{ minHeight: 300, fontSize: 12 }}
                value={form.diff_text} onChange={e => setForm({ ...form, diff_text: e.target.value })} />
            </div>
          </div>
        )}

        {mode === "pr" && (
          <div>
            <div style={{ padding: 12, background: "rgba(210,153,34,0.1)", border: "1px solid rgba(210,153,34,0.2)", borderRadius: 8, marginBottom: 16 }}>
              <p style={{ fontSize: 13, color: "var(--warning)" }}>
                ⚠️ Requires <code style={{ background: "var(--bg3)", padding: "1px 6px", borderRadius: 4 }}>GITHUB_TOKEN</code> environment variable configured on the server.
              </p>
            </div>
            <div className="grid-2" style={{ marginBottom: 16 }}>
              <div>
                <label className="label">Repository</label>
                <input className="input" placeholder="owner/repo-name"
                  value={form.repo_name} onChange={e => setForm({ ...form, repo_name: e.target.value })} />
              </div>
              <div>
                <label className="label">PR Number</label>
                <input className="input" type="number" placeholder="42"
                  value={form.pr_number} onChange={e => setForm({ ...form, pr_number: e.target.value })} />
              </div>
            </div>
          </div>
        )}

        {error && <p className="error-msg" style={{ marginBottom: 12 }}>{error}</p>}

        <button className="btn btn-primary" onClick={submit} disabled={loading}
          style={{ minWidth: 160, justifyContent: "center" }}>
          {loading ? <><span className="spinner" /> Starting review...</> : "🤖 Run AI Review"}
        </button>

        <div style={{ marginTop: 16, padding: 12, background: "var(--bg3)", borderRadius: 8, fontSize: 12, color: "var(--text2)", lineHeight: 1.7 }}>
          <strong style={{ color: "var(--text)" }}>Pipeline:</strong> Analyzer Agent (CodeBERT + FAISS) → Reviewer Agent (LLM + RAG) → Reporter Agent (GitHub comment) → MLflow tracking
        </div>
      </div>
    </div>
  );
}
