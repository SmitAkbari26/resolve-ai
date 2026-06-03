import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  LayoutDashboard,
  Ticket,
  GitBranch,
  ShieldCheck,
  Bell,
  Bot,
  AlertTriangle,
  MessagesSquare,
  MessageSquare,
  BookOpen,
  LogOut,
  Sparkles,
  Layout,
  Home,
} from "lucide-react";

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuth();
  const role = user?.role || "customer";
  const onLogout = logout;
  const navigate = useNavigate();
  const location = useLocation();

  const adminLinks = [
    { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { name: "Tickets", path: "/tickets", icon: Ticket },
    { name: "Conversations", path: "/conversations", icon: MessagesSquare },
    { name: "Workflows", path: "/workflows", icon: GitBranch },
    { name: "Approvals", path: "/approvals", icon: ShieldCheck },
    { name: "Escalations", path: "/escalations", icon: AlertTriangle },
    { name: "Notifications", path: "/notifications", icon: Bell },
    { name: "Agents", path: "/agents", icon: Bot },
    { name: "Policies", path: "/policies", icon: ShieldCheck },
    { name: "Knowledge Base", path: "/knowledge", icon: BookOpen },
    { name: "Tenants", path: "/tenants", icon: Home },
    { name: "Widget", path: "/widget", icon: Layout },
  ];

  const customerLinks = [
    { name: "Customer Chat", path: "/chat", icon: MessageSquare },
  ];

  const links = role === "admin" ? adminLinks : customerLinks;

  return (
    <aside className="w-64 bg-[#090d1f]/90 text-white flex flex-col h-screen select-none border-r border-slate-800/80 shadow-2xl backdrop-blur-xl">
      {/* Brand logo */}
      <div className="p-6 flex items-center gap-3 border-b border-slate-800/60 bg-indigo-950/10">
        <div className="bg-indigo-500/20 text-indigo-400 p-2 rounded-xl shadow-inner border border-indigo-500/30">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <h1 className="font-extrabold text-base tracking-wide text-slate-100">
            Resolve AI
          </h1>
          <span className="text-[10px] text-indigo-400 font-bold uppercase tracking-wider block mt-0.5">
            Orchestrator
          </span>
        </div>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        <div className="text-[10px] font-extrabold text-slate-500 uppercase tracking-widest px-3 mb-2">
          Management
        </div>
        {links.map((link) => {
          const Icon = link.icon;
          const isActive = location.pathname === link.path;
          return (
            <button
              key={link.path}
              onClick={() => navigate(link.path)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 group ${
                isActive
                  ? "bg-indigo-600/15 text-indigo-300 border-l-4 border-indigo-500 pl-2 bg-gradient-to-r from-indigo-500/10 to-transparent shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.02]"
              }`}
            >
              <Icon
                className={`w-4 h-4 transition-transform duration-200 ${
                  isActive
                    ? "text-indigo-400"
                    : "text-slate-500 group-hover:scale-105"
                }`}
              />
              <span>{link.name}</span>
            </button>
          );
        })}
      </nav>

      {/* User Status / Logout */}
      <div className="p-4 border-t border-slate-800/60 bg-[#060a17]/50">
        <div className="flex items-center justify-between mb-3 px-2">
          <div className="flex flex-col">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
              Session
            </span>
            <span className="text-xs font-semibold text-indigo-400 capitalize font-mono mt-0.5">
              {role} Mode
            </span>
          </div>
        </div>
        <button
          onClick={onLogout}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 hover:text-rose-350 rounded-xl text-xs font-semibold border border-rose-500/20 transition-all shadow-sm"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
};
