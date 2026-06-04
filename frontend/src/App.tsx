import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import type { UserRole } from "./context/AuthContext";

import { Layout }        from "./components/Layout";
import { Login }         from "./pages/Login";
import { Register }      from "./pages/Register";
import { Dashboard }     from "./pages/Dashboard";
import { Tickets }       from "./pages/Tickets";
import { Workflows }     from "./pages/Workflows";
import { Approvals }     from "./pages/Approvals";
import { Notifications } from "./pages/Notifications";
import { Chat }          from "./pages/Chat";
import { KnowledgeBase } from "./pages/KnowledgeBase";
import { Conversations } from "./pages/Conversations";
import { Escalations }   from "./pages/Escalations";
import { Agents }        from "./pages/Agents";
import { Policies }      from "./pages/Policies";
import Widget            from "./pages/Widget";
import Tenants           from "./pages/Tenants";

import { Unauthorized } from "./pages/Unauthorized";

/* ─── Default landing per role ───────────────────────────── */
const DEFAULT_ROUTE: Record<UserRole, string> = {
  admin:    "/dashboard",
  manager:  "/dashboard",
  agent:    "/conversations",
  customer: "/chat",
};

/* ─── Route guard: only allow specific roles ─────────────── */
interface GuardProps {
  allowed: UserRole[];
  role: UserRole;
  children: React.ReactNode;
}
const Guard: React.FC<GuardProps> = ({ allowed, role, children }) =>
  allowed.includes(role) ? <>{children}</> : <Navigate to="/unauthorized" replace />;


/* ─── Main routes ─────────────────────────────────────────── */
const AppRoutes: React.FC = () => {
  const { user, isAuthenticated, login } = useAuth();
  const role: UserRole = (user?.role as UserRole) ?? "customer";

  return (
    <Routes>
      {/* ── Public ───────────────────────────────────────── */}
      <Route
        path="/login"
        element={
          isAuthenticated
            ? <Navigate to={DEFAULT_ROUTE[role]} replace />
            : <Login onLoginSuccess={login} />
        }
      />
      <Route
        path="/register"
        element={
          isAuthenticated
            ? <Navigate to={DEFAULT_ROUTE[role]} replace />
            : <Register />
        }
      />

      {/* ── Private (requires auth) ───────────────────────── */}
      {isAuthenticated && role ? (
        <Route
          path="/*"
          element={
            <Layout>
              <Routes>
                {/* ── Admin-only ──────────────────────────── */}
                <Route path="/tenants" element={
                  <Guard allowed={["admin"]} role={role}><Tenants /></Guard>
                } />
                <Route path="/widget" element={
                  <Guard allowed={["admin"]} role={role}><Widget /></Guard>
                } />
                <Route path="/policies" element={
                  <Guard allowed={["admin"]} role={role}><Policies /></Guard>
                } />
                <Route path="/workflows" element={
                  <Guard allowed={["admin"]} role={role}><Workflows /></Guard>
                } />
                <Route path="/approvals" element={
                  <Guard allowed={["admin"]} role={role}><Approvals /></Guard>
                } />

                {/* ── Admin + Manager ─────────────────────── */}
                <Route path="/dashboard" element={
                  <Guard allowed={["admin", "manager"]} role={role}><Dashboard /></Guard>
                } />
                <Route path="/agents" element={
                  <Guard allowed={["admin", "manager"]} role={role}><Agents /></Guard>
                } />

                {/* ── Admin + Manager + Agent ─────────────── */}
                <Route path="/tickets" element={
                  <Guard allowed={["admin", "manager", "agent"]} role={role}><Tickets /></Guard>
                } />
                <Route path="/conversations" element={
                  <Guard allowed={["admin", "manager", "agent"]} role={role}><Conversations /></Guard>
                } />
                <Route path="/escalations" element={
                  <Guard allowed={["admin", "manager", "agent"]} role={role}><Escalations /></Guard>
                } />
                <Route path="/notifications" element={
                  <Guard allowed={["admin", "manager", "agent"]} role={role}><Notifications /></Guard>
                } />
                <Route path="/knowledge" element={
                  <Guard allowed={["admin", "manager", "agent"]} role={role}><KnowledgeBase /></Guard>
                } />

                {/* ── Customer only ────────────────────────── */}
                <Route path="/chat" element={
                  <Guard allowed={["customer"]} role={role}><Chat /></Guard>
                } />

                {/* ── Unauthorized ────────────────────────── */}
                <Route path="/unauthorized" element={<Unauthorized />} />

                {/* ── Catch-all: redirect to role default ─── */}
                <Route path="*" element={<Navigate to={DEFAULT_ROUTE[role]} replace />} />
              </Routes>
            </Layout>
          }
        />
      ) : (
        <Route path="*" element={<Navigate to="/login" replace />} />
      )}
    </Routes>
  );
};

export const App: React.FC = () => (
  <AuthProvider>
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  </AuthProvider>
);

export default App;
