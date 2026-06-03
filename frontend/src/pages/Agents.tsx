import React, { useEffect, useState, useMemo } from "react";
import { agentApi, ticketApi } from "../services/api";
import {
  Bot,
  RefreshCw,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Cpu,
  Activity,
  Ticket,
  BarChart2,
} from "lucide-react";

interface AgentRow {
  id: string;
  name: string;
  agent_type: string;
  model_name?: string | null;
  status: string;
  description?: string | null;
}

interface TicketRow {
  id: string;
  assigned_agent?: string | null;
  status: string;
  priority: string;
  summary: string;
}

export const Agents: React.FC = () => {
  const [agents, setAgents] = useState<AgentRow[]>([]);
  const [tickets, setTickets] = useState<TicketRow[]>([]);
  const [statusFilter, setStatusFilter] = useState("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);

  const ITEMS_PER_PAGE = 6;

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [agentData, ticketData] = await Promise.all([
        agentApi.listAgents(statusFilter),
        ticketApi.listTickets(),
      ]);
      setAgents(Array.isArray(agentData) ? agentData : []);
      setTickets(Array.isArray(ticketData) ? ticketData : []);
    } catch {
      setError("Failed to load agents");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setPage(1);
    load();
  }, [statusFilter]);

  // Build per-agent ticket counts from tickets list
  const agentTicketMap = useMemo(() => {
    const map: Record<string, { open: number; total: number }> = {};
    for (const t of tickets) {
      const name = t.assigned_agent?.toLowerCase().trim();
      if (!name) continue;
      if (!map[name]) map[name] = { open: 0, total: 0 };
      map[name].total++;
      if (t.status !== "closed" && t.status !== "resolved") map[name].open++;
    }
    return map;
  }, [tickets]);

  const maxOpenTickets = useMemo(
    () => Math.max(1, ...Object.values(agentTicketMap).map((v) => v.open)),
    [agentTicketMap],
  );

  const totalPages = Math.ceil(agents.length / ITEMS_PER_PAGE);
  const paginatedAgents = agents.slice(
    (page - 1) * ITEMS_PER_PAGE,
    page * ITEMS_PER_PAGE,
  );

  const getStatusStyle = (status: string) => {
    if (status === "active")
      return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
    return "bg-rose-500/20 text-rose-400 border-rose-500/30";
  };

  const getWorkloadColor = (open: number, max: number) => {
    const ratio = open / max;
    if (ratio >= 0.75) return "bg-rose-500";
    if (ratio >= 0.4) return "bg-amber-500";
    return "bg-emerald-500";
  };

  const activeCount = agents.filter((a) => a.status === "active").length;
  const inactiveCount = agents.filter((a) => a.status === "inactive").length;
  const totalOpenTickets = tickets.filter(
    (t) => t.status !== "closed" && t.status !== "resolved",
  ).length;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-3">
            <Bot className="w-7 h-7 text-cyan-400" />
            AI Agents
          </h1>
          <p className="text-slate-400 mt-1">
            Monitor agents and their live ticket workload
          </p>
        </div>

        <div className="flex gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-2xl px-4 py-3 text-slate-200 transition"
          >
            <option className="bg-[#0b1120]" value="all">
              All Statuses
            </option>
            <option className="bg-[#0b1120]" value="active">
              Active
            </option>
            <option className="bg-[#0b1120]" value="inactive">
              Inactive
            </option>
          </select>

          <button
            onClick={load}
            className="flex items-center gap-2 px-4 py-2 border border-slate-800 bg-[#090d1f]/40 hover:bg-[#090d1f]/80 text-slate-200 text-xs font-semibold rounded-xl transition-all"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`}
            />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        {[
          { label: "Total Agents", value: agents.length, icon: Bot, color: "text-cyan-400" },
          { label: "Active", value: activeCount, icon: Activity, color: "text-emerald-400" },
          { label: "Inactive", value: inactiveCount, icon: Cpu, color: "text-rose-400" },
          { label: "Open Tickets", value: totalOpenTickets, icon: Ticket, color: "text-amber-400" },
        ].map((stat, i) => (
          <div
            key={i}
            className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6 hover:border-cyan-500/50 transition-all"
          >
            <stat.icon className={`w-6 h-6 ${stat.color} mb-3`} />
            <p className="text-slate-400 text-sm">{stat.label}</p>
            <h3 className="text-3xl font-bold text-white mt-2">{stat.value}</h3>
          </div>
        ))}
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 text-rose-300 border border-rose-700 bg-rose-900/20 px-4 py-3 rounded-2xl">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {/* Agent Cards */}
      {loading ? (
        <div className="grid gap-5">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="h-44 bg-slate-900 border border-slate-800 rounded-3xl animate-pulse"
            />
          ))}
        </div>
      ) : paginatedAgents.length > 0 ? (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
          {paginatedAgents.map((a) => {
            const agentKey = a.name.toLowerCase().trim();
            const counts = agentTicketMap[agentKey] ?? { open: 0, total: 0 };
            const workloadPct = Math.round((counts.open / maxOpenTickets) * 100);

            return (
              <div
                key={a.id}
                className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6 hover:border-cyan-500/60 transition-all duration-300 space-y-4"
              >
                {/* Top row */}
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-slate-100">{a.name}</h3>
                    <p className="text-xs text-slate-500 font-mono mt-0.5">
                      {a.id.slice(0, 8)}…
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-xl text-xs border ${getStatusStyle(a.status)}`}
                  >
                    {a.status}
                  </span>
                </div>

                {/* Details grid */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-slate-900 border border-slate-800 rounded-2xl p-3">
                    <p className="text-xs text-slate-500 mb-1">Agent Type</p>
                    <p className="text-slate-200 text-sm">{a.agent_type}</p>
                  </div>
                  <div className="bg-slate-900 border border-slate-800 rounded-2xl p-3">
                    <p className="text-xs text-slate-500 mb-1">Model</p>
                    <p className="text-slate-200 text-sm">{a.model_name || "—"}</p>
                  </div>
                </div>

                {/* Workload section */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-xs text-slate-400">
                      <BarChart2 className="w-3.5 h-3.5 text-cyan-500" />
                      <span>Ticket Workload</span>
                    </div>
                    <div className="flex gap-3 text-xs">
                      <span className="text-amber-400 font-semibold">
                        {counts.open} open
                      </span>
                      <span className="text-slate-500">/ {counts.total} total</span>
                    </div>
                  </div>

                  {/* Workload bar */}
                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${getWorkloadColor(counts.open, maxOpenTickets)}`}
                      style={{ width: `${workloadPct}%` }}
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-12 text-center text-slate-500">
          No agents found.
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-4">
          <button
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
            className="p-3 bg-slate-800 rounded-xl disabled:opacity-40"
          >
            <ChevronLeft className="w-4 h-4 text-white" />
          </button>

          <span className="text-slate-300 text-sm">
            Page {page} of {totalPages}
          </span>

          <button
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="p-3 bg-slate-800 rounded-xl disabled:opacity-40"
          >
            <ChevronRight className="w-4 h-4 text-white" />
          </button>
        </div>
      )}
    </div>
  );
};
