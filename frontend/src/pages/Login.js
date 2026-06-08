import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authAPI } from "../services/api";
import { useAuth } from "../App";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true); setError("");
    try {
      const res = await authAPI.login(form);
      login(res.data.user, res.data.access_token);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    } finally { setLoading(false); }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg)" }}>
      <div style={{ width: "100%", maxWidth: 400, padding: 16 }}>
        <div className="card" style={{ padding: "2rem" }}>
          <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
            <div style={{ fontSize: 36, marginBottom: 8 }}>🤖</div>
            <h1 style={{ fontSize: 22, fontWeight: 700 }}>AI Code Reviewer</h1>
            <p style={{ color: "var(--text2)", fontSize: 13, marginTop: 4 }}>Multi-agent code review powered by LangGraph</p>
          </div>
          <form onSubmit={submit}>
            <div style={{ marginBottom: 14 }}>
              <label className="label">Email</label>
              <input className="input" type="email" placeholder="you@email.com"
                value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
            </div>
            <div style={{ marginBottom: 18 }}>
              <label className="label">Password</label>
              <input className="input" type="password" placeholder="••••••••"
                value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
            </div>
            {error && <p className="error-msg" style={{ marginBottom: 12 }}>{error}</p>}
            <button className="btn btn-primary" type="submit" disabled={loading}
              style={{ width: "100%", justifyContent: "center" }}>
              {loading ? <span className="spinner" /> : "Sign In"}
            </button>
          </form>
          <p style={{ textAlign: "center", marginTop: 16, fontSize: 13, color: "var(--text2)" }}>
            No account? <Link to="/register" style={{ color: "var(--primary)" }}>Create one</Link>
          </p>
          <div style={{ marginTop: 20, padding: 12, background: "var(--bg3)", borderRadius: 8, fontSize: 12, color: "var(--text2)" }}>
            <div style={{ fontWeight: 500, marginBottom: 4, color: "var(--text)" }}>Stack</div>
            LangGraph · CodeBERT · FAISS · MLflow · LangSmith · OpenRouter · FastAPI
          </div>
        </div>
      </div>
    </div>
  );
}
