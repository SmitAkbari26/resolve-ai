import React, { useEffect, useState } from "react";
import { conversationApi } from "../services/api";
import {
  MessagesSquare,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  MessageCircle,
  User,
  Activity,
} from "lucide-react";

interface Conversation {
  id: string;
  user_id: string;
  channel: string;
  sentiment: string;
  status: string;
  created_at: string;
}

export const Conversations: React.FC = () => {
  const [rows, setRows] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);

  const ITEMS_PER_PAGE = 6;

  const load = async () => {
    setLoading(true);
    try {
      const data = await conversationApi.listConversations();
      setRows(Array.isArray(data) ? data : []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const totalPages = Math.ceil(rows.length / ITEMS_PER_PAGE);

  const paginatedRows = rows.slice(
    (page - 1) * ITEMS_PER_PAGE,
    page * ITEMS_PER_PAGE,
  );

  const getStatusStyle = (status: string) => {
    if (status === "resolved")
      return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";

    if (status === "pending")
      return "bg-amber-500/20 text-amber-400 border-amber-500/30";

    return "bg-slate-700/30 text-slate-300 border-slate-600";
  };

  const getSentimentStyle = (sentiment: string) => {
    if (sentiment === "positive") return "text-emerald-400";
    if (sentiment === "negative") return "text-rose-400";
    return "text-amber-400";
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-3">
            <MessagesSquare className="w-7 h-7 text-indigo-400" />
            Conversations
          </h1>
          <p className="text-slate-400 mt-1">
            Track and monitor support conversations
          </p>
        </div>

        <button
          onClick={load}
          className="flex items-center gap-2 px-4 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-2xl text-slate-200 transition"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {/* Cards */}
      {loading ? (
        <div className="grid gap-5">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="h-36 bg-slate-900 border border-slate-800 rounded-3xl animate-pulse"
            />
          ))}
        </div>
      ) : paginatedRows.length > 0 ? (
        <div className="grid gap-5">
          {paginatedRows.map((r) => (
            <div
              key={r.id}
              className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6 hover:border-indigo-500 transition-all duration-300"
            >
              <div className="flex justify-between items-start">
                <div className="space-y-4 flex-1">
                  <div className="flex items-center gap-3">
                    <MessageCircle className="w-5 h-5 text-indigo-400" />
                    <p className="font-mono text-xs text-slate-400 truncate">
                      {r.id}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-5">
                    <div>
                      <p className="text-xs text-slate-500 mb-1">User</p>
                      <p className="text-slate-200 text-sm flex items-center gap-2">
                        <User className="w-4 h-4" />
                        {r.user_id}
                      </p>
                    </div>

                    <div>
                      <p className="text-xs text-slate-500 mb-1">Channel</p>
                      <p className="text-slate-200">{r.channel}</p>
                    </div>

                    <div>
                      <p className="text-xs text-slate-500 mb-1">Sentiment</p>
                      <p
                        className={`capitalize font-medium ${getSentimentStyle(
                          r.sentiment,
                        )}`}
                      >
                        {r.sentiment}
                      </p>
                    </div>

                    <div>
                      <p className="text-xs text-slate-500 mb-1">Status</p>
                      <span
                        className={`px-3 py-1 rounded-xl text-xs border ${getStatusStyle(
                          r.status,
                        )}`}
                      >
                        {r.status}
                      </span>
                    </div>
                  </div>
                </div>

                <Activity className="w-5 h-5 text-slate-600" />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-12 text-center text-slate-500">
          No conversations found.
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
