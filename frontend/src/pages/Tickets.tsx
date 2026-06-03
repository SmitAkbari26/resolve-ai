import React, { useState, useEffect } from "react";
import { ticketApi, agentApi, commentApi, historyApi } from "../services/api";
import { useAuth } from "../context/AuthContext";
import {
  Search,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  MessageSquare,
  History,
  Lock,
  Unlock,
  User,
  Calendar,
  Send
} from "lucide-react";

interface Ticket {
  id: string;
  summary: string;
  description: string;
  status: string;
  priority: string;
  assigned_agent?: string | null;
  resolution?: string | null;
}

interface Agent {
  id: string;
  name: string;
}

interface TicketComment {
  id: string;
  ticket_id: string;
  user_id: string;
  comment: string;
  is_internal: boolean;
  created_at: string;
}

interface TicketHistory {
  id: string;
  ticket_id: string;
  field_name: string;
  old_value: string | null;
  new_value: string | null;
  changed_by: string | null;
  changed_at: string;
}

export const Tickets: React.FC = () => {
  const { user } = useAuth();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [editingAgents, setEditingAgents] = useState<Record<string, string>>({});
  const [editingStatuses, setEditingStatuses] = useState<Record<string, string>>({});
  const [editingResolutions, setEditingResolutions] = useState<Record<string, string>>({});
  const [updatingTicketId, setUpdatingTicketId] = useState<string | null>(null);
  const [updateSuccessMsg, setUpdateSuccessMsg] = useState<string | null>(null);

  // Collapsible & Tabs
  const [expandedTicketId, setExpandedTicketId] = useState<string | null>(null);
  const [comments, setComments] = useState<Record<string, TicketComment[]>>({});
  const [histories, setHistories] = useState<Record<string, TicketHistory[]>>({});
  const [activeTab, setActiveTab] = useState<Record<string, "comments" | "audit">>({});
  const [newComments, setNewComments] = useState<Record<string, string>>({});
  const [isInternalComment, setIsInternalComment] = useState<Record<string, boolean>>({});

  const [currentPage, setCurrentPage] = useState(1);
  const ITEMS_PER_PAGE = 4;

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const ticketData = await ticketApi.listTickets(statusFilter);
      const agentData = await agentApi.listAgents();

      const list = Array.isArray(ticketData)
        ? ticketData
        : (ticketData?.data ?? []);

      setTickets(list);
      setAgents(Array.isArray(agentData) ? agentData : []);

      const agentsMap: Record<string, string> = {};
      const statusesMap: Record<string, string> = {};
      const resolutionsMap: Record<string, string> = {};

      list.forEach((t: Ticket) => {
        agentsMap[t.id] = t.assigned_agent || "";
        statusesMap[t.id] = t.status;
        resolutionsMap[t.id] = t.resolution || "";
      });

      setEditingAgents(agentsMap);
      setEditingStatuses(statusesMap);
      setEditingResolutions(resolutionsMap);
    } catch {
      setError("Failed to load ticket data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setCurrentPage(1);
    fetchData();
  }, [statusFilter]);

  const handleUpdateTicket = async (ticketId: string) => {
    setUpdatingTicketId(ticketId);

    try {
      await ticketApi.updateTicket(ticketId, {
        assigned_agent: editingAgents[ticketId],
        status: editingStatuses[ticketId],
        resolution: editingResolutions[ticketId],
      });

      setUpdateSuccessMsg("Ticket updated successfully");
      setTimeout(() => setUpdateSuccessMsg(null), 2500);

      fetchData();
      if (expandedTicketId === ticketId) {
        loadHistory(ticketId);
      }
    } catch {
      setError("Failed updating ticket");
    } finally {
      setUpdatingTicketId(null);
    }
  };

  const loadComments = async (ticketId: string) => {
    try {
      const res = await commentApi.listComments(ticketId);
      setComments((prev) => ({ ...prev, [ticketId]: res }));
    } catch (err) {
      console.error("Failed to load comments", err);
    }
  };

  const loadHistory = async (ticketId: string) => {
    try {
      const res = await historyApi.listHistory(ticketId);
      setHistories((prev) => ({ ...prev, [ticketId]: res }));
    } catch (err) {
      console.error("Failed to load history", err);
    }
  };

  const toggleExpandTicket = (ticketId: string) => {
    if (expandedTicketId === ticketId) {
      setExpandedTicketId(null);
    } else {
      setExpandedTicketId(ticketId);
      if (!activeTab[ticketId]) {
        setActiveTab((prev) => ({ ...prev, [ticketId]: "comments" }));
      }
      loadComments(ticketId);
      loadHistory(ticketId);
    }
  };

  const handleAddComment = async (ticketId: string) => {
    const text = newComments[ticketId] || "";
    if (!text.trim()) return;

    const userId = user?.id || "00000000-0000-0000-0000-000000000000";
    const isInternal = !!isInternalComment[ticketId];

    try {
      await commentApi.createComment({
        ticket_id: ticketId,
        user_id: userId,
        comment: text,
        is_internal: isInternal,
      });

      setNewComments((prev) => ({ ...prev, [ticketId]: "" }));
      loadComments(ticketId);
    } catch (err) {
      setError("Failed to add comment");
      setTimeout(() => setError(null), 3000);
    }
  };

  const filteredTickets = tickets.filter((ticket) => {
    const matchesPriority =
      priorityFilter === "all" || ticket.priority === priorityFilter;

    const matchesSearch =
      !searchQuery ||
      ticket.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.id.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesPriority && matchesSearch;
  });

  const totalPages = Math.ceil(filteredTickets.length / ITEMS_PER_PAGE);

  const paginatedTickets = filteredTickets.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE,
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case "resolved":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
      case "in_progress":
        return "bg-blue-500/10 text-blue-400 border-blue-500/20";
      case "open":
        return "bg-cyan-500/10 text-cyan-400 border-cyan-500/20";
      case "escalated":
        return "bg-rose-500/10 text-rose-400 border-rose-500/20";
      case "pending_customer":
        return "bg-amber-500/10 text-amber-400 border-amber-500/20";
      case "pending_approval":
        return "bg-purple-500/10 text-purple-400 border-purple-500/20";
      case "closed":
        return "bg-slate-600/10 text-slate-400 border-slate-600/20";
      default:
        return "bg-slate-500/10 text-slate-400 border-slate-500/20";
    }
  };

  const totalCount = tickets.length;
  const openCount = tickets.filter((t) => t.status === "open").length;
  const progressCount = tickets.filter((t) => t.status === "in_progress").length;
  const escalatedCount = tickets.filter((t) => t.status === "escalated").length;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
            Ticket Center
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Zendesk-Style Ticket Orchestration and Auditing Dashboard.
          </p>
        </div>

        <button
          onClick={fetchData}
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
          { label: "Total Tickets", value: totalCount },
          { label: "Open", value: openCount },
          { label: "In Progress", value: progressCount },
          { label: "Escalated", value: escalatedCount },
        ].map((stat, i) => (
          <div key={i} className="glass-card p-5 rounded-2xl">
            <div className="card-glow" />
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
              {stat.label}
            </span>
            <span className="text-2xl font-bold mt-1 block text-slate-100">
              {stat.value}
            </span>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="glass-card p-5 rounded-2xl grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
        <div className="card-glow" />

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="w-full bg-[#0d1329]/80 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
        >
          <option className="bg-[#090d1f]" value="all">
            All Statuses
          </option>
          <option className="bg-[#090d1f]" value="open">
            Open
          </option>
          <option className="bg-[#090d1f]" value="in_progress">
            In Progress
          </option>
          <option className="bg-[#090d1f]" value="pending_customer">
            Pending Customer
          </option>
          <option className="bg-[#090d1f]" value="pending_approval">
            Pending Approval
          </option>
          <option className="bg-[#090d1f]" value="resolved">
            Resolved
          </option>
          <option className="bg-[#090d1f]" value="closed">
            Closed
          </option>
          <option className="bg-[#090d1f]" value="escalated">
            Escalated
          </option>
        </select>

        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          className="w-full bg-[#0d1329]/80 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
        >
          <option className="bg-[#090d1f]" value="all">
            All Priorities
          </option>
          <option className="bg-[#090d1f]" value="critical">
            Critical
          </option>
          <option className="bg-[#090d1f]" value="high">
            High
          </option>
          <option className="bg-[#090d1f]" value="medium">
            Medium
          </option>
          <option className="bg-[#090d1f]" value="low">
            Low
          </option>
        </select>

        <div className="relative">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search summary or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#0d1329]/80 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {/* Alerts */}
      {updateSuccessMsg && (
        <div className="bg-emerald-950/20 border border-emerald-800/40 text-emerald-400 p-4 rounded-xl text-sm">
          {updateSuccessMsg}
        </div>
      )}

      {error && (
        <div className="bg-rose-950/20 border border-rose-800/40 text-rose-400 p-4 rounded-xl text-sm">
          {error}
        </div>
      )}

      {/* Ticket Cards */}
      <div className="grid grid-cols-1 gap-6">
        {paginatedTickets.map((ticket) => {
          const isExpanded = expandedTicketId === ticket.id;
          const ticketComments = comments[ticket.id] || [];
          const ticketHistories = histories[ticket.id] || [];
          const currentTab = activeTab[ticket.id] || "comments";

          return (
            <div
              key={ticket.id}
              className="glass-card rounded-2xl overflow-hidden border border-slate-800/50 hover:border-slate-800 transition-all duration-300"
            >
              <div className="card-glow" />

              {/* Main Ticket Summary Row */}
              <div
                onClick={() => toggleExpandTicket(ticket.id)}
                className="p-5 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 cursor-pointer hover:bg-slate-900/10 transition-all select-none"
              >
                <div className="flex-grow space-y-1">
                  <div className="flex items-center gap-3">
                    <span
                      className={`text-[9px] font-extrabold uppercase px-2.5 py-0.5 border rounded-full ${getStatusColor(ticket.status)}`}
                    >
                      {ticket.status.replace(/_/g, " ")}
                    </span>
                    <span className="text-[10px] font-bold text-slate-500 tracking-wider">
                      {ticket.priority.toUpperCase()} PRIORITY
                    </span>
                  </div>
                  <h3 className="font-semibold text-slate-200 text-lg">
                    {ticket.summary}
                  </h3>
                  <p className="text-xs font-mono text-slate-500">
                    ID: {ticket.id}
                  </p>
                </div>

                <div className="flex items-center gap-4 self-stretch md:self-auto justify-between md:justify-start">
                  <div className="text-right text-xs">
                    <p className="text-slate-400">
                      Agent:{" "}
                      <span className="text-indigo-400">
                        {ticket.assigned_agent || "Unassigned"}
                      </span>
                    </p>
                  </div>
                  <div className="p-2 border border-slate-800 rounded-xl hover:bg-slate-800 transition">
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                </div>
              </div>

              {/* Expanded details container */}
              {isExpanded && (
                <div className="border-t border-slate-800/50 bg-[#070b19]/60 p-5 space-y-6">
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left Column: Properties / Update Form */}
                    <div className="space-y-4 lg:col-span-1 border-r border-slate-800/50 pr-0 lg:pr-6">
                      <h4 className="text-xs font-extrabold text-slate-400 uppercase tracking-widest">
                        Ticket Properties
                      </h4>

                      <div className="space-y-3">
                        <div>
                          <label className="text-[10px] font-bold text-slate-500 uppercase block mb-1">
                            Assign Agent
                          </label>
                          <select
                            value={editingAgents[ticket.id]}
                            onChange={(e) =>
                              setEditingAgents({
                                ...editingAgents,
                                [ticket.id]: e.target.value,
                              })
                            }
                            className="w-full bg-[#0d1329]/80 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                          >
                            <option className="bg-[#090d1f]" value="">
                              Assign Agent
                            </option>
                            {agents.map((agent) => (
                              <option
                                key={agent.id}
                                className="bg-[#090d1f]"
                                value={agent.name}
                              >
                                {agent.name}
                              </option>
                            ))}
                          </select>
                        </div>

                        <div>
                          <label className="text-[10px] font-bold text-slate-500 uppercase block mb-1">
                            Status
                          </label>
                          <select
                            value={editingStatuses[ticket.id]}
                            onChange={(e) =>
                              setEditingStatuses({
                                ...editingStatuses,
                                [ticket.id]: e.target.value,
                              })
                            }
                            className="w-full bg-[#0d1329]/80 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                          >
                            <option className="bg-[#090d1f]" value="open">
                              Open
                            </option>
                            <option className="bg-[#090d1f]" value="in_progress">
                              In Progress
                            </option>
                            <option className="bg-[#090d1f]" value="pending_customer">
                              Pending Customer
                            </option>
                            <option className="bg-[#090d1f]" value="pending_approval">
                              Pending Approval
                            </option>
                            <option className="bg-[#090d1f]" value="resolved">
                              Resolved
                            </option>
                            <option className="bg-[#090d1f]" value="closed">
                              Closed
                            </option>
                            <option className="bg-[#090d1f]" value="escalated">
                              Escalated
                            </option>
                          </select>
                        </div>

                        <div>
                          <label className="text-[10px] font-bold text-slate-500 uppercase block mb-1">
                            Resolution Details
                          </label>
                          <textarea
                            value={editingResolutions[ticket.id]}
                            placeholder="Resolution details or internal response notes..."
                            onChange={(e) =>
                              setEditingResolutions({
                                ...editingResolutions,
                                [ticket.id]: e.target.value,
                              })
                            }
                            className="w-full bg-[#0d1329]/80 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 min-h-[80px] focus:outline-none focus:border-indigo-500 placeholder:text-slate-600"
                          />
                        </div>

                        <button
                          disabled={updatingTicketId === ticket.id}
                          onClick={() => handleUpdateTicket(ticket.id)}
                          className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-600/50 text-white font-semibold text-xs rounded-xl transition"
                        >
                          {updatingTicketId === ticket.id ? "Saving..." : "Submit Ticket Changes"}
                        </button>
                      </div>

                      <div className="pt-4 border-t border-slate-800/40">
                        <span className="text-[10px] font-bold text-slate-500 uppercase block mb-1">
                          Original Description
                        </span>
                        <p className="text-xs text-slate-300 bg-[#050814]/40 border border-slate-800/40 rounded-xl p-3 max-h-[150px] overflow-y-auto whitespace-pre-wrap">
                          {ticket.description || "No description provided."}
                        </p>
                      </div>
                    </div>

                    {/* Right Columns: Comments vs History */}
                    <div className="lg:col-span-2 flex flex-col space-y-4">
                      {/* Tabs Bar */}
                      <div className="flex border-b border-slate-850">
                        <button
                          onClick={() =>
                            setActiveTab((prev) => ({ ...prev, [ticket.id]: "comments" }))
                          }
                          className={`flex items-center gap-2 px-4 py-2 text-xs font-semibold border-b-2 transition ${
                            currentTab === "comments"
                              ? "border-indigo-500 text-indigo-400"
                              : "border-transparent text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          <MessageSquare className="w-3.5 h-3.5" />
                          Comment History ({ticketComments.length})
                        </button>
                        <button
                          onClick={() =>
                            setActiveTab((prev) => ({ ...prev, [ticket.id]: "audit" }))
                          }
                          className={`flex items-center gap-2 px-4 py-2 text-xs font-semibold border-b-2 transition ${
                            currentTab === "audit"
                              ? "border-indigo-500 text-indigo-400"
                              : "border-transparent text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          <History className="w-3.5 h-3.5" />
                          Audit Log ({ticketHistories.length})
                        </button>
                      </div>

                      {/* Comments Tab content */}
                      {currentTab === "comments" && (
                        <div className="flex-grow flex flex-col space-y-4">
                          {/* Comments Stream */}
                          <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
                            {ticketComments.length === 0 ? (
                              <p className="text-xs text-slate-500 italic p-4 text-center">
                                No comments added to this ticket yet.
                              </p>
                            ) : (
                              ticketComments.map((comment) => (
                                <div
                                  key={comment.id}
                                  className={`rounded-xl border p-3.5 space-y-2 text-xs ${
                                    comment.is_internal
                                      ? "bg-[#ffb700]/5 border-[#ffb700]/20"
                                      : "bg-slate-900/30 border-slate-800"
                                  }`}
                                >
                                  <div className="flex justify-between items-center">
                                    <div className="flex items-center gap-2">
                                      <div
                                        className={`p-1.5 rounded-lg ${
                                          comment.is_internal
                                            ? "bg-[#ffb700]/10 text-[#ffb700]"
                                            : "bg-slate-800 text-slate-300"
                                        }`}
                                      >
                                        {comment.is_internal ? (
                                          <Lock className="w-3 h-3" />
                                        ) : (
                                          <Unlock className="w-3 h-3" />
                                        )}
                                      </div>
                                      <span className="font-semibold text-slate-300">
                                        {comment.is_internal ? "Internal Note" : "Public Reply"}
                                      </span>
                                      <span className="text-[10px] text-slate-500">
                                        by user {comment.user_id.slice(0, 8)}
                                      </span>
                                    </div>
                                    <span className="text-[10px] text-slate-500">
                                      {new Date(comment.created_at).toLocaleString()}
                                    </span>
                                  </div>
                                  <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">
                                    {comment.comment}
                                  </p>
                                </div>
                              ))
                            )}
                          </div>

                          {/* Add Comment Input Form */}
                          <div className="bg-[#0b1022] border border-slate-800/80 rounded-xl p-3 space-y-3">
                            <textarea
                              value={newComments[ticket.id] || ""}
                              onChange={(e) =>
                                setNewComments((prev) => ({
                                  ...prev,
                                  [ticket.id]: e.target.value,
                                }))
                              }
                              placeholder="Write a comment..."
                              className="w-full bg-slate-950/40 border border-slate-800/60 rounded-lg p-2.5 text-xs text-slate-300 min-h-[60px] focus:outline-none focus:border-indigo-500 placeholder:text-slate-600"
                            />

                            <div className="flex justify-between items-center">
                              <label className="flex items-center gap-2 cursor-pointer select-none">
                                <input
                                  type="checkbox"
                                  checked={!!isInternalComment[ticket.id]}
                                  onChange={(e) =>
                                    setIsInternalComment((prev) => ({
                                      ...prev,
                                      [ticket.id]: e.target.checked,
                                    }))
                                  }
                                  className="rounded border-slate-800 text-indigo-500 bg-[#0d1329] focus:ring-indigo-500"
                                />
                                <span className="text-[11px] text-slate-400 flex items-center gap-1 font-semibold">
                                  {isInternalComment[ticket.id] ? (
                                    <>
                                      <Lock className="w-3 h-3 text-[#ffb700]" />
                                      Internal Note
                                    </>
                                  ) : (
                                    <>
                                      <Unlock className="w-3 h-3 text-slate-500" />
                                      Public Reply
                                    </>
                                  )}
                                </span>
                              </label>

                              <button
                                onClick={() => handleAddComment(ticket.id)}
                                className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-lg transition"
                              >
                                <Send className="w-3 h-3" />
                                Submit Note
                              </button>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Audit History Tab content */}
                      {currentTab === "audit" && (
                        <div className="space-y-2 max-h-[350px] overflow-y-auto pr-1">
                          {ticketHistories.length === 0 ? (
                            <p className="text-xs text-slate-500 italic p-4 text-center">
                              No history updates recorded for this ticket yet.
                            </p>
                          ) : (
                            ticketHistories.map((event) => (
                              <div
                                key={event.id}
                                className="bg-[#050814]/30 border border-slate-800/40 rounded-xl p-3 text-xs flex justify-between items-start gap-4"
                              >
                                <div className="space-y-1">
                                  <p className="text-slate-300">
                                    Updated{" "}
                                    <span className="font-semibold text-indigo-400">
                                      {event.field_name}
                                    </span>
                                  </p>
                                  <div className="flex items-center gap-2 text-[10px] text-slate-400">
                                    <span className="line-through text-slate-600">
                                      {event.old_value || "None"}
                                    </span>
                                    <span>&rarr;</span>
                                    <span className="text-slate-300 font-medium">
                                      {event.new_value || "None"}
                                    </span>
                                  </div>
                                </div>
                                <div className="text-right text-[10px] text-slate-500 space-y-0.5">
                                  <p className="flex items-center justify-end gap-1">
                                    <User className="w-2.5 h-2.5" />
                                    {event.changed_by || "system"}
                                  </p>
                                  <p className="flex items-center justify-end gap-1">
                                    <Calendar className="w-2.5 h-2.5" />
                                    {new Date(event.changed_at).toLocaleString()}
                                  </p>
                                </div>
                              </div>
                            ))
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-4">
          <button
            disabled={currentPage === 1}
            onClick={() => setCurrentPage((p) => p - 1)}
            className="p-3 bg-white/[0.05] rounded-xl border border-white/10 hover:bg-white/10 disabled:opacity-40 transition"
          >
            <ChevronLeft />
          </button>

          <span className="text-slate-300 text-sm">
            Page {currentPage} of {totalPages}
          </span>

          <button
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage((p) => p + 1)}
            className="p-3 bg-white/[0.05] rounded-xl border border-white/10 hover:bg-white/10 disabled:opacity-40 transition"
          >
            <ChevronRight />
          </button>
        </div>
      )}
    </div>
  );
};

