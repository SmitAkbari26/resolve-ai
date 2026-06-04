import React from "react";
import { useNavigate } from "react-router-dom";
import { ShieldAlert, ArrowLeft } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import type { UserRole } from "../context/AuthContext";

const DEFAULT_ROUTE: Record<UserRole, string> = {
  admin: "/dashboard",
  manager: "/dashboard",
  agent: "/conversations",
  customer: "/chat",
};

export const Unauthorized: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const role = (user?.role as UserRole) ?? "customer";
  const homePath = DEFAULT_ROUTE[role] || "/login";

  return (
    <div className="min-h-screen bg-[#080B16] flex items-center justify-center p-4">
      <div className="relative max-w-md w-full bg-[#0F1326]/70 border border-red-500/30 rounded-3xl p-8 text-center backdrop-blur-xl shadow-2xl overflow-hidden group">
        {/* Glow Effects */}
        <div className="absolute -top-24 -left-24 w-48 h-48 bg-red-500/10 rounded-full blur-3xl group-hover:bg-red-500/15 transition-all duration-500" />
        <div className="absolute -bottom-24 -right-24 w-48 h-48 bg-indigo-500/10 rounded-full blur-3xl group-hover:bg-indigo-500/15 transition-all duration-500" />

        {/* Icon */}
        <div className="mx-auto w-16 h-16 bg-red-500/10 border border-red-500/20 text-red-400 flex items-center justify-center rounded-2xl mb-6 shadow-inner animate-pulse">
          <ShieldAlert className="w-8 h-8" />
        </div>

        {/* Header */}
        <h1 className="text-2xl font-extrabold text-white tracking-tight mb-2">
          Access Restricted
        </h1>
        <p className="text-sm text-slate-400 mb-8 leading-relaxed">
          You do not have the required permissions to view this resource. Please contact your administrator if you believe this is an error.
        </p>

        {/* Actions */}
        <div className="space-y-3">
          <button
            onClick={() => navigate(homePath)}
            className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-2xl font-semibold shadow-lg shadow-indigo-600/20 hover:shadow-indigo-500/30 transition-all duration-200"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Go Back Home</span>
          </button>
        </div>
      </div>
    </div>
  );
};
