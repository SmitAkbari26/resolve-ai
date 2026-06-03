import React, { useState, useEffect } from "react";
import { notificationApi, apiClient } from "../services/api";
import {
  Bell,
  Search,
  RefreshCw,
  Send,
  CheckCircle2,
  Mail,
  MessageCircle,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

interface NotificationLog {
  id: string;
  user_id: string;
  ticket_id?: string | null;
  subject: string;
  message: string;
  status: string;
  channel: string;
}

export const Notifications: React.FC = () => {
  const [notifications, setNotifications] = useState<NotificationLog[]>([]);
  const [statusFilter, setStatusFilter] = useState("all");
  const [channelFilter, setChannelFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryingId, setRetryingId] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const [currentPage, setCurrentPage] = useState(1);
  const ITEMS_PER_PAGE = 8;

  const fetchNotifications = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await notificationApi.listNotifications(statusFilter);
      setNotifications(Array.isArray(data) ? data : (data?.data ?? []));
    } catch (err: any) {
      setError("Failed to fetch notification logs. Please verify backend.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setCurrentPage(1);
    fetchNotifications();
  }, [statusFilter]);

  const handleRetry = async (notificationId: string) => {
    setRetryingId(notificationId);
    setError(null);
    setSuccessMsg(null);
    try {
      await apiClient.put(`/notifications/${notificationId}`, {
        status: "pending",
      });
      setSuccessMsg(`Retry initiated for notification ${notificationId}`);
      setTimeout(() => setSuccessMsg(null), 3000);
      fetchNotifications();
    } catch (err: any) {
      setError(`Failed to retry delivery for notification ${notificationId}`);
    } finally {
      setRetryingId(null);
    }
  };

  const filteredNotifications = notifications.filter((notif) => {
    const matchesChannel =
      channelFilter === "all" || notif.channel === channelFilter;
    const matchesSearch =
      !searchQuery ||
      notif.user_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (notif.ticket_id &&
        notif.ticket_id.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesChannel && matchesSearch;
  });

  const totalPages = Math.ceil(filteredNotifications.length / ITEMS_PER_PAGE);

  const paginatedNotifications = filteredNotifications.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE,
  );

  const totalCount = notifications.length;
  const sentCount = notifications.filter(
    (n) => n.status === "sent" || n.status === "read",
  ).length;
  const failedCount = notifications.filter((n) => n.status === "failed").length;
  const pendingCount = notifications.filter(
    (n) => n.status === "pending",
  ).length;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "sent":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
      case "read":
        return "bg-blue-500/10 text-blue-400 border-blue-500/20";
      case "failed":
        return "bg-rose-500/10 text-rose-400 border-rose-500/20";
      default:
        return "bg-amber-500/10 text-amber-400 border-amber-500/20";
    }
  };

  const getChannelIcon = (channel: string) => {
    switch (channel.toLowerCase()) {
      case "email":
        return <Mail className="w-3.5 h-3.5" />;
      case "sms":
        return <MessageCircle className="w-3.5 h-3.5" />;
      default:
        return <Bell className="w-3.5 h-3.5" />;
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
            Notification Center
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Monitor automated notifications, alert channels, delivery states and
            failures.
          </p>
        </div>
        <button
          onClick={fetchNotifications}
          className="flex items-center gap-2 px-4 py-2 border border-slate-800 bg-[#090d1f]/40 hover:bg-[#090d1f]/80 text-slate-200 text-xs font-semibold rounded-xl transition-all"
        >
          <RefreshCw
            className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`}
          />
          Refresh
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: "Total Logs", value: totalCount, color: "text-slate-100" },
          { label: "Delivered", value: sentCount, color: "text-emerald-400" },
          { label: "Pending", value: pendingCount, color: "text-amber-400" },
          {
            label: "Failed Deliveries",
            value: failedCount,
            color: "text-rose-400",
          },
        ].map((stat, i) => (
          <div key={i} className="glass-card p-5 rounded-2xl">
            <div className="card-glow" />
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
              {stat.label}
            </span>
            <span className={`text-2xl font-bold mt-1 block ${stat.color}`}>
              {stat.value}
            </span>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="glass-card p-5 rounded-2xl grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
        <div className="card-glow" />
        <div className="space-y-1.5 z-10">
          <label className="text-xs font-semibold text-slate-400 block">
            Status Filter
          </label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full bg-[#0d1329]/80 border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 text-slate-200 transition-all"
          >
            <option className="bg-[#090d1f]" value="all">
              All Statuses
            </option>
            <option className="bg-[#090d1f]" value="pending">
              Pending
            </option>
            <option className="bg-[#090d1f]" value="sent">
              Sent
            </option>
            <option className="bg-[#090d1f]" value="failed">
              Failed
            </option>
            <option className="bg-[#090d1f]" value="read">
              Read
            </option>
          </select>
        </div>

        <div className="space-y-1.5 z-10">
          <label className="text-xs font-semibold text-slate-400 block">
            Channel Filter
          </label>
          <select
            value={channelFilter}
            onChange={(e) => setChannelFilter(e.target.value)}
            className="w-full bg-[#0d1329]/80 border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 text-slate-200 transition-all"
          >
            <option className="bg-[#090d1f]" value="all">
              All Channels
            </option>
            <option className="bg-[#090d1f]" value="email">
              Email
            </option>
            <option className="bg-[#090d1f]" value="sms">
              SMS
            </option>
            <option className="bg-[#090d1f]" value="slack">
              Slack
            </option>
            <option className="bg-[#090d1f]" value="push">
              Push Notification
            </option>
          </select>
        </div>

        <div className="space-y-1.5 z-10">
          <label className="text-xs font-semibold text-slate-400 block">
            Search User / Ticket ID
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#0d1329]/80 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-sm focus:outline-none focus:border-indigo-500 text-slate-200 transition-all"
            />
          </div>
        </div>
      </div>

      {successMsg && (
        <div className="bg-emerald-950/20 border border-emerald-800/40 text-emerald-400 p-4 rounded-xl text-sm flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-500" />
          <span>{successMsg}</span>
        </div>
      )}

      {error && (
        <div className="bg-rose-950/20 border border-rose-800/40 text-rose-400 p-4 rounded-xl text-sm flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-rose-500" />
          <span>{error}</span>
        </div>
      )}

      {/* List */}
      {loading ? (
        <div className="text-center py-12 text-slate-500 text-sm">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-slate-600" />
          Loading notifications...
        </div>
      ) : paginatedNotifications.length === 0 ? (
        <div className="glass-card rounded-2xl p-12 text-center text-slate-500">
          <div className="card-glow" />
          <Bell className="w-8 h-8 mx-auto mb-3 text-slate-600" />
          No notifications found matching the criteria.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {paginatedNotifications.map((notif) => (
            <div
              key={notif.id}
              className="glass-card rounded-2xl overflow-hidden flex flex-col hover:border-indigo-500/30 transition-all duration-200"
            >
              <div className="card-glow" />
              <div className="p-5 space-y-3.5 z-10">
                {/* Header */}
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-0.5">
                    <h3 className="font-bold text-slate-200 text-sm">
                      {notif.subject || "System Notification"}
                    </h3>
                    <span className="text-[10px] text-slate-500 block">
                      User ID:{" "}
                      <span className="font-mono">{notif.user_id}</span>
                    </span>
                  </div>
                  <span
                    className={`text-[9px] font-extrabold uppercase tracking-wider px-2 py-0.5 border rounded-full ${getStatusBadge(notif.status)}`}
                  >
                    {notif.status}
                  </span>
                </div>

                {/* Message */}
                <p className="text-xs text-slate-400 bg-[#0d1329]/50 border border-slate-800 rounded-xl p-3">
                  {notif.message}
                </p>
              </div>

              {/* Footer */}
              <div className="px-5 py-4 border-t border-slate-800/30 flex items-center justify-between text-[11px] text-slate-500 font-semibold z-10">
                <span className="flex items-center gap-1.5 capitalize text-slate-400">
                  {getChannelIcon(notif.channel)}
                  {notif.channel}
                </span>
                {notif.ticket_id && (
                  <span className="font-mono bg-slate-800/40 text-slate-400 px-2 py-0.5 rounded border border-slate-700/40">
                    Ticket: {notif.ticket_id}
                  </span>
                )}
                {notif.status === "failed" && (
                  <button
                    disabled={retryingId === notif.id}
                    onClick={() => handleRetry(notif.id)}
                    className="flex items-center gap-1 px-3 py-1 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-[10px] font-bold shadow transition-colors disabled:opacity-50"
                  >
                    {retryingId === notif.id ? (
                      <RefreshCw className="w-3 h-3 animate-spin" />
                    ) : (
                      <Send className="w-3 h-3" />
                    )}
                    Retry
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-4">
          <button
            disabled={currentPage === 1}
            onClick={() => setCurrentPage((p) => p - 1)}
            className="p-3 bg-white/[0.05] rounded-xl border border-white/10"
          >
            <ChevronLeft />
          </button>

          <span className="text-slate-300">
            Page {currentPage} of {totalPages}
          </span>

          <button
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage((p) => p + 1)}
            className="p-3 bg-white/[0.05] rounded-xl border border-white/10"
          >
            <ChevronRight />
          </button>
        </div>
      )}
    </div>
  );
};
