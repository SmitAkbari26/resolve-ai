import React from "react";
import { Sidebar } from "./Sidebar";
import { Calendar, Server } from "lucide-react";
import { useAuth } from "../context/AuthContext";

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  useAuth();
  const [isOnline, setIsOnline] = React.useState<boolean | null>(null);

  const currentDateString = new Date().toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  React.useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch("http://localhost:8000/health");
        if (res.ok) {
          setIsOnline(true);
        } else {
          setIsOnline(false);
        }
      } catch {
        setIsOnline(false);
      }
    };
    checkHealth();
    const timer = setInterval(checkHealth, 50000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-transparent">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Topbar Header */}
        <header className="h-16 bg-[#040817]/40 border-b border-slate-800/50 px-8 flex items-center justify-between shrink-0 backdrop-blur-md">
          <div className="flex items-center gap-3">
            {isOnline === null ? (
              <span className="text-[10px] font-bold bg-slate-500/10 text-slate-400 px-3 py-1 rounded-full border border-slate-550/20 flex items-center gap-1.5 shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-pulse"></span>
                Checking API Status...
              </span>
            ) : isOnline ? (
              <span className="text-[10px] font-bold bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full border border-emerald-500/20 flex items-center gap-1.5 shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                API Online
              </span>
            ) : (
              <span className="text-[10px] font-bold bg-rose-500/10 text-rose-400 px-3 py-1 rounded-full border border-rose-500/20 flex items-center gap-1.5 shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse"></span>
                API Offline
              </span>
            )}
          </div>

          <div className="flex items-center gap-6 text-slate-450 text-xs font-semibold">
            <span className="flex items-center gap-1.5 text-slate-400">
              <Calendar className="w-3.5 h-3.5 text-indigo-400" />
              {currentDateString}
            </span>
            <span className="flex items-center gap-1.5 text-slate-400 font-mono">
              <Server className="w-3.5 h-3.5 text-indigo-400" />
              v1.0.0
            </span>
          </div>
        </header>

        {/* Content Viewport */}
        <main className="flex-1 overflow-y-auto p-4">
          <div className="max-w-8xl mx-auto space-y-8">{children}</div>
        </main>
      </div>
    </div>
  );
};
