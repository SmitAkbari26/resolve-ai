import React, { useEffect, useState } from "react";
import { escalationApi } from "../services/api";
import {
  AlertTriangle,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

interface Escalation {
  id: string;
  ticket_id: string;
  escalation_type: string;
  reason: string;
  status: string;
  created_at: string;
}

export const Escalations: React.FC = () => {
  const [rows, setRows] = useState<Escalation[]>([]);
  const [statusFilter, setStatusFilter] = useState("all");
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);

  const ITEMS_PER_PAGE = 6;

  const load = async () => {
    setLoading(true);
    try {
      const data = await escalationApi.listEscalations(statusFilter);
      setRows(Array.isArray(data) ? data : []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setPage(1);
    load();
  }, [statusFilter]);

  const totalPages = Math.ceil(rows.length / ITEMS_PER_PAGE);

  const paginatedRows = rows.slice(
    (page - 1) * ITEMS_PER_PAGE,
    page * ITEMS_PER_PAGE,
  );

  const getStatusStyle = (status: string) => {
    if (status === "resolved")
      return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";

    if (status === "rejected")
      return "bg-rose-500/20 text-rose-400 border-rose-500/30";

    return "bg-amber-500/20 text-amber-400 border-amber-500/30";
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-3">
            <AlertTriangle className="w-7 h-7 text-amber-400" />
            Escalations
          </h1>
          <p className="text-slate-400 mt-1">Monitor escalated support cases</p>
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
            <option className="bg-[#0b1120]" value="pending">
              Pending
            </option>
            <option className="bg-[#0b1120]" value="resolved">
              Resolved
            </option>
            <option className="bg-[#0b1120]" value="rejected">
              Rejected
            </option>
          </select>

          <button
            onClick={load}
            className="flex items-center gap-2 px-4 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-2xl text-slate-200 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Cards */}
      {loading ? (
        <div className="grid gap-5">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="h-40 bg-slate-900 border border-slate-800 rounded-3xl animate-pulse"
            />
          ))}
        </div>
      ) : paginatedRows.length > 0 ? (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
          {paginatedRows.map((e) => (
            <div
              key={e.id}
              className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6 hover:border-amber-500 transition-all duration-300"
            >
              <div className="flex justify-between items-start mb-5">
                <div>
                  <h3 className="font-semibold text-slate-100">
                    {e.escalation_type}
                  </h3>
                  <p className="text-xs text-slate-500 font-mono">{e.id}</p>
                </div>

                <span
                  className={`px-3 py-1 rounded-xl text-xs border ${getStatusStyle(
                    e.status,
                  )}`}
                >
                  {e.status}
                </span>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 mb-4">
                <p className="text-slate-300 text-sm">{e.reason}</p>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-slate-500 mb-1">Ticket</p>
                  <p className="text-slate-200 font-mono">{e.ticket_id}</p>
                </div>

                <div>
                  <p className="text-slate-500 mb-1">Created</p>
                  <p className="text-slate-200">{e.created_at}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-12 text-center text-slate-500">
          No escalations found.
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
