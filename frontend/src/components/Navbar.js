import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../App";

const NAV = [
  { path: "/", label: "Dashboard" },
  { path: "/reviews", label: "Reviews" },
  { path: "/new-review", label: "+ New Review" },
  { path: "/analytics", label: "Analytics" },
];

export default function Navbar() {
  const { pathname } = useLocation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <nav style={{
      background: "var(--bg2)", borderBottom: "1px solid var(--border)",
      padding: "0 24px", display: "flex", alignItems: "center",
      justifyContent: "space-between", height: 56, position: "sticky", top: 0, zIndex: 100,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 32 }}>
        <Link to="/" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 18, fontWeight: 700 }}>
            <span style={{ color: "var(--primary)" }}>AI</span>
            <span style={{ color: "var(--text)" }}> Code Reviewer</span>
          </span>
        </Link>
        <div style={{ display: "flex", gap: 4 }}>
          {NAV.map(item => (
            <Link key={item.path} to={item.path} style={{
              textDecoration: "none", padding: "6px 12px", borderRadius: 6,
              fontSize: 13, fontWeight: 500,
              color: pathname === item.path ? "var(--primary)" : "var(--text2)",
              background: pathname === item.path ? "rgba(56,139,253,0.1)" : "transparent",
              border: item.label.startsWith("+") ? "1px solid var(--border)" : "none",
            }}>
              {item.label}
            </Link>
          ))}
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <span style={{ fontSize: 12, color: "var(--text2)" }}>
          <span style={{ color: "var(--success)" }}>●</span> {user?.name}
        </span>
        <button onClick={() => { logout(); navigate("/login"); }}
          style={{ background: "none", border: "1px solid var(--border)", color: "var(--text2)",
            padding: "4px 12px", borderRadius: 6, fontSize: 12, cursor: "pointer" }}>
          Logout
        </button>
      </div>
    </nav>
  );
}
