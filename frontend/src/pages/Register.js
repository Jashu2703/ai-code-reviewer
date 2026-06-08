import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authAPI } from "../services/api";
import { useAuth } from "../App";

export default function Register() {
  const [form, setForm] = useState({ name: "", email: "", password: "", github_username: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true); setError("");
    try {
      const res = await authAPI.register(form);
      login(res.data.user, res.data.access_token);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    } finally { setLoading(false); }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg)" }}>
      <div style={{ width: "100%", maxWidth: 420, padding: 16 }}>
        <div className="card" style={{ padding: "2rem" }}>
          <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
            <div style={{ fontSize: 36, marginBottom: 8 }}>🤖</div>
            <h1 style={{ fontSize: 22, fontWeight: 700 }}>Create Account</h1>
            <p style={{ color: "var(--text2)", fontSize: 13 }}>Start reviewing code with AI</p>
          </div>
          <form onSubmit={submit}>
            <div style={{ marginBottom: 14 }}>
              <label className="label">Full Name</label>
              <input className="input" placeholder="Jashwanth Valasa"
                value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            </div>
            <div style={{ marginBottom: 14 }}>
              <label className="label">Email</label>
              <input className="input" type="email" placeholder="you@email.com"
                value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
            </div>
            <div style={{ marginBottom: 14 }}>
              <label className="label">GitHub Username <span style={{ color: "var(--text3)" }}>(optional)</span></label>
              <input className="input" placeholder="Jashu2703"
                value={form.github_username} onChange={(e) => setForm({ ...form, github_username: e.target.value })} />
            </div>
            <div style={{ marginBottom: 18 }}>
              <label className="label">Password</label>
              <input className="input" type="password" placeholder="Min 6 characters"
                value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required minLength={6} />
            </div>
            {error && <p className="error-msg" style={{ marginBottom: 12 }}>{error}</p>}
            <button className="btn btn-primary" type="submit" disabled={loading}
              style={{ width: "100%", justifyContent: "center" }}>
              {loading ? <span className="spinner" /> : "Create Account"}
            </button>
          </form>
          <p style={{ textAlign: "center", marginTop: 16, fontSize: 13, color: "var(--text2)" }}>
            Already have an account? <Link to="/login" style={{ color: "var(--primary)" }}>Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
