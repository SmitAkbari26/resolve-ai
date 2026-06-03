import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { Dashboard } from "./pages/Dashboard";
import { Tickets } from "./pages/Tickets";
import { Workflows } from "./pages/Workflows";
import { Approvals } from "./pages/Approvals";
import { Notifications } from "./pages/Notifications";
import { Chat } from "./pages/Chat";
import { KnowledgeBase } from "./pages/KnowledgeBase";
import { Conversations } from "./pages/Conversations";
import { Escalations } from "./pages/Escalations";
import { Agents } from "./pages/Agents";
import { Policies } from "./pages/Policies";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Widget from "./pages/Widget";
import Tenants from "./pages/Tenants";

const AppRoutes: React.FC = () => {
  const { user, isAuthenticated, login } = useAuth();
  const role = user?.role || null;

  return (
    <Routes>
      {/* Auth Routes */}
      <Route
        path="/login"
        element={
          isAuthenticated ? (
            <Navigate to={role === "admin" ? "/dashboard" : "/chat"} replace />
          ) : (
            <Login onLoginSuccess={login} />
          )
        }
      />
      <Route
        path="/register"
        element={
          isAuthenticated ? (
            <Navigate to={role === "admin" ? "/dashboard" : "/chat"} replace />
          ) : (
            <Register />
          )
        }
      />

      {/* Private Routes wrapped in Layout */}
      {isAuthenticated && role ? (
        <Route
          path="/*"
          element={
            <Layout>
              <Routes>
                {role === "admin" ? (
                  <>
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/tickets" element={<Tickets />} />
                    <Route path="/conversations" element={<Conversations />} />
                    <Route path="/workflows" element={<Workflows />} />
                    <Route path="/approvals" element={<Approvals />} />
                    <Route path="/escalations" element={<Escalations />} />
                    <Route path="/notifications" element={<Notifications />} />
                    <Route path="/agents" element={<Agents />} />
                    <Route path="/policies" element={<Policies />} />
                    <Route path="/knowledge" element={<KnowledgeBase />} />
                    <Route path="/widget" element={<Widget />} />
                    <Route path="/tenants" element={<Tenants />} />
                    <Route
                      path="*"
                      element={<Navigate to="/dashboard" replace />}
                    />
                  </>
                ) : (
                  <>
                    <Route path="/chat" element={<Chat />} />
                    <Route path="*" element={<Navigate to="/chat" replace />} />
                  </>
                )}
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

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
