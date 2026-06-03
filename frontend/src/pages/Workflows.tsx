import React, { useState, useEffect } from "react";
import { workflowApi } from "../services/api";
import {
  Search,
  RefreshCw,
  GitBranch,
  AlertCircle,
  XCircle,
  Play,
  ChevronDown,
  ChevronUp,
  Cpu,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

interface Workflow {
  id: string;
  workflow_type: string;
  ticket_id: string;
  status: string;
  current_step: string;
}

interface WorkflowStep {
  id: string;
  step_name: string;
  agent_id?: string;
  status: string;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
}

export const Workflows: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [statusFilter, setStatusFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const ITEMS_PER_PAGE = 5;

  // Inspector States
  const [inspectorId, setInspectorId] = useState("");
  const [inspectedWf, setInspectedWf] = useState<Workflow | null>(null);
  const [inspectedSteps, setInspectedSteps] = useState<WorkflowStep[]>([]);
  const [inspectLoading, setInspectLoading] = useState(false);

  // Accordion details states (storing step details for workflow IDs)
  const [expandedWorkflows, setExpandedWorkflows] = useState<
    Record<string, boolean>
  >({});
  const [workflowStepsMap, setWorkflowStepsMap] = useState<
    Record<string, WorkflowStep[]>
  >({});
  const [loadingSteps, setLoadingSteps] = useState<Record<string, boolean>>({});

  const fetchWorkflows = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await workflowApi.listExecutions(statusFilter);
      // Safety checks matching original Streamlit parsing
      if (Array.isArray(data)) {
        setWorkflows(data);
      } else if (data && Array.isArray(data.data)) {
        setWorkflows(data.data);
      } else {
        setWorkflows([]);
      }
    } catch (err: any) {
      setError(
        "Failed to fetch workflows. Please verify backend service is running.",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setCurrentPage(1);
    fetchWorkflows();
  }, [statusFilter]);

  const toggleWorkflowExpand = async (workflowId: string) => {
    const isCurrentlyExpanded = !!expandedWorkflows[workflowId];
    setExpandedWorkflows({
      ...expandedWorkflows,
      [workflowId]: !isCurrentlyExpanded,
    });

    if (!isCurrentlyExpanded && !workflowStepsMap[workflowId]) {
      setLoadingSteps({ ...loadingSteps, [workflowId]: true });
      try {
        const steps = await workflowApi.listSteps(workflowId);
        setWorkflowStepsMap({ ...workflowStepsMap, [workflowId]: steps });
      } catch (err) {
        console.error("Failed to load steps for workflow", workflowId);
      } finally {
        setLoadingSteps({ ...loadingSteps, [workflowId]: false });
      }
    }
  };

  const handleInspect = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inspectorId) return;

    setInspectLoading(true);
    setInspectedWf(null);
    setInspectedSteps([]);
    setError(null);

    try {
      const wfDetail = await workflowApi.getExecution(inspectorId);
      const steps = await workflowApi.listSteps(inspectorId);
      setInspectedWf(wfDetail);
      setInspectedSteps(steps);
    } catch (err: any) {
      setError(
        `Failed to inspect workflow ID: ${inspectorId}. Double check the ID.`,
      );
    } finally {
      setInspectLoading(false);
    }
  };

  const handleQuickInspect = async (workflow: Workflow) => {
    setInspectorId(workflow.id);
    setInspectLoading(true);
    setError(null);
    try {
      const steps = await workflowApi.listSteps(workflow.id);
      setInspectedWf(workflow);
      setInspectedSteps(steps);
      document
        .getElementById("workflow-inspector")
        ?.scrollIntoView({ behavior: "smooth" });
    } catch (err) {
      setError(`Failed to inspect steps for workflow ${workflow.id}`);
    } finally {
      setInspectLoading(false);
    }
  };

  const handleAction = async (workflowId: string, newStatus: string) => {
    try {
      const axiosInstance = (await import("../services/api")).apiClient;
      await axiosInstance.put(`/workflow-executions/${workflowId}`, {
        status: newStatus,
      });
      fetchWorkflows();
      if (inspectedWf && inspectedWf.id === workflowId) {
        setInspectedWf({ ...inspectedWf, status: newStatus });
      }
    } catch (err) {
      setError(`Failed to update workflow ${workflowId}`);
    }
  };

  const filteredWorkflows = workflows.filter((wf) => {
    const matchesType =
      typeFilter === "all" ||
      wf.workflow_type.toLowerCase().includes(typeFilter.toLowerCase());
    const matchesSearch =
      !searchQuery ||
      wf.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      wf.ticket_id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  const totalPages = Math.ceil(filteredWorkflows.length / ITEMS_PER_PAGE);

  const paginatedWorkflows = filteredWorkflows.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE,
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
      case "running":
        return "bg-blue-500/10 text-blue-400 border-blue-500/20";
      case "paused":
        return "bg-amber-500/10 text-amber-400 border-amber-500/20";
      case "waiting_approval":
        return "bg-purple-500/10 text-purple-400 border-purple-500/20";
      case "failed":
        return "bg-rose-500/10 text-rose-400 border-rose-500/20";
      default:
        return "bg-slate-500/10 text-slate-400 border-slate-500/20";
    }
  };

  const totalCount = workflows.length;
  const runningCount = workflows.filter((w) => w.status === "running").length;
  const pausedCount = workflows.filter(
    (w) => w.status === "paused" || w.status === "waiting_approval",
  ).length;
  const failedCount = workflows.filter((w) => w.status === "failed").length;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
            Workflow Monitor
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Track autonomic agent orchestrations, pipeline executions, and
            detailed timelines.
          </p>
        </div>
        <button
          onClick={fetchWorkflows}
          className="flex items-center gap-2 px-4 py-2 border border-slate-800 bg-[#090d1f]/40 hover:bg-[#090d1f]/80 text-slate-200 text-xs font-semibold rounded-xl transition-all"
        >
          <RefreshCw
            className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`}
          />
          Refresh
        </button>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          {
            label: "Total Executions",
            value: totalCount,
            color: "text-slate-100",
          },
          { label: "Running", value: runningCount, color: "text-blue-400" },
          {
            label: "Paused / Waiting",
            value: pausedCount,
            color: "text-purple-400",
          },
          { label: "Failed", value: failedCount, color: "text-rose-400" },
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

      {/* Filters Card */}
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
            <option className="bg-[#090d1f]" value="running">
              Running
            </option>
            <option className="bg-[#090d1f]" value="waiting_approval">
              Waiting Approval
            </option>
            <option className="bg-[#090d1f]" value="completed">
              Completed
            </option>
            <option className="bg-[#090d1f]" value="failed">
              Failed
            </option>
            <option className="bg-[#090d1f]" value="cancelled">
              Cancelled
            </option>
          </select>
        </div>

        <div className="space-y-1.5 z-10">
          <label className="text-xs font-semibold text-slate-400 block">
            Workflow Type Filter
          </label>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="w-full bg-[#0d1329]/80 border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 text-slate-200 transition-all"
          >
            <option className="bg-[#090d1f]" value="all">
              All Types
            </option>
            <option className="bg-[#090d1f]" value="refund">
              Refund Workflows
            </option>
            <option className="bg-[#090d1f]" value="general">
              General Support Workflows
            </option>
            <option className="bg-[#090d1f]" value="technical">
              Technical Support Workflows
            </option>
          </select>
        </div>

        <div className="space-y-1.5 z-10">
          <label className="text-xs font-semibold text-slate-400 block">
            Search Ticket / Workflow ID
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

      {error && (
        <div className="bg-rose-950/20 border border-rose-800/40 text-rose-400 p-4 rounded-xl text-sm flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-rose-500" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-7 space-y-6">
          <div className="glass-card rounded-2xl overflow-hidden">
            <div className="card-glow" />
            <div className="px-6 py-4 border-b border-slate-800/50 bg-[#0d1329]/40 flex items-center justify-between z-10 relative">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Active Executions
              </span>
              <span className="text-[10px] font-bold bg-indigo-550/20 text-indigo-400 px-2 py-0.5 rounded-full border border-indigo-500/20">
                {filteredWorkflows.length} Found
              </span>
            </div>

            {loading ? (
              <div className="p-12 text-center text-slate-500 text-sm">
                <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-slate-450" />
                Loading workflows...
              </div>
            ) : filteredWorkflows.length === 0 ? (
              <div className="p-12 text-center text-slate-500 z-10 relative">
                <GitBranch className="w-8 h-8 mx-auto mb-3 text-slate-400" />
                No workflow executions found.
              </div>
            ) : (
              <div className="divide-y divide-slate-800/50 z-10 relative">
                {paginatedWorkflows.map((wf) => (
                  <div
                    key={wf.id}
                    className="p-6 space-y-4 hover:bg-white/[0.01] transition-colors"
                  >
                    {/* Header Row */}
                    <div className="flex items-start justify-between gap-4">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-slate-200 text-sm">
                            {wf.workflow_type}
                          </span>
                          <span
                            className={`text-[9px] font-extrabold uppercase px-2 py-0.5 border rounded-full ${getStatusColor(wf.status)}`}
                          >
                            {wf.status.replace(/_/g, " ")}
                          </span>
                        </div>
                        <span className="text-xs font-mono text-slate-500 block">
                          Workflow ID: {wf.id}
                        </span>
                      </div>
                      <button
                        onClick={() => handleQuickInspect(wf)}
                        className="text-xs font-bold text-indigo-400 hover:text-indigo-300 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 px-3 py-1.5 rounded-xl transition-colors"
                      >
                        Inspect Steps
                      </button>
                    </div>

                    <div className="text-xs text-slate-350">
                      Current Step:{" "}
                      <strong className="text-slate-200 capitalize">
                        {(wf.current_step ?? "not started").replace(/_/g, " ")}
                      </strong>
                      <span className="text-slate-500 font-mono ml-4">
                        Ticket: {wf.ticket_id}
                      </span>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-3 select-none pt-2 border-t border-slate-800/30">
                      {wf.status === "failed" && (
                        <button
                          onClick={() => handleAction(wf.id, "running")}
                          className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold shadow transition-colors"
                        >
                          <Play className="w-3 h-3" />
                          Retry Workflow
                        </button>
                      )}

                      {(wf.status === "running" ||
                        wf.status === "waiting_approval" ||
                        wf.status === "paused") && (
                        <button
                          onClick={() => handleAction(wf.id, "cancelled")}
                          className="flex items-center gap-1.5 px-3 py-1.5 bg-rose-500/10 border border-rose-500/30 hover:bg-rose-500/20 text-rose-400 rounded-xl text-xs font-semibold transition-colors"
                        >
                          <XCircle className="w-3 h-3" />
                          Cancel Workflow
                        </button>
                      )}

                      <button
                        onClick={() => toggleWorkflowExpand(wf.id)}
                        className="ml-auto flex items-center gap-1 text-slate-500 hover:text-slate-300 text-xs font-medium py-1 px-2 hover:bg-white/[0.02] rounded transition-colors"
                      >
                        <span>Timeline</span>
                        {expandedWorkflows[wf.id] ? (
                          <ChevronUp className="w-3.5 h-3.5" />
                        ) : (
                          <ChevronDown className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </div>

                    {/* Timeline Collapsed Panel */}
                    {expandedWorkflows[wf.id] && (
                      <div className="mt-4 p-4 bg-[#080c1d]/60 rounded-2xl border border-slate-800 animate-fadeIn">
                        <span className="text-[10px] font-bold text-slate-550 uppercase tracking-wider block mb-3">
                          Workflow steps trace
                        </span>
                        {loadingSteps[wf.id] ? (
                          <div className="text-xs text-slate-500 py-3 flex items-center gap-2">
                            <RefreshCw className="w-3 h-3 animate-spin text-slate-500" />
                            Tracing step pipeline...
                          </div>
                        ) : !workflowStepsMap[wf.id] ||
                          workflowStepsMap[wf.id].length === 0 ? (
                          <div className="text-xs text-slate-550 py-3">
                            No steps registered for this workflow.
                          </div>
                        ) : (
                          <div className="space-y-3 relative pl-4 border-l border-slate-800 ml-1.5">
                            {workflowStepsMap[wf.id].map((step, idx) => (
                              <div key={step.id} className="relative text-xs">
                                <span
                                  className={`absolute -left-[21px] top-1.5 w-2 h-2 rounded-full border border-[#0d1329] ${
                                    step.status === "completed"
                                      ? "bg-emerald-500"
                                      : step.status === "running"
                                        ? "bg-blue-500 animate-pulse"
                                        : step.status === "failed"
                                          ? "bg-rose-500"
                                          : "bg-slate-500"
                                  }`}
                                />
                                <div className="flex justify-between font-medium">
                                  <span className="text-slate-300">
                                    {idx + 1}. {step.step_name}
                                  </span>
                                  <span
                                    className={`text-[8px] uppercase px-1.5 rounded font-extrabold ${
                                      step.status === "completed"
                                        ? "text-emerald-450 bg-emerald-500/10 border border-emerald-500/20"
                                        : step.status === "running"
                                          ? "text-blue-450 bg-blue-500/10 border border-blue-500/20 animate-pulse"
                                          : step.status === "failed"
                                            ? "text-rose-450 bg-rose-500/10 border border-rose-500/20"
                                            : "text-slate-400 bg-slate-500/10 border border-slate-500/20"
                                    }`}
                                  >
                                    {step.status}
                                  </span>
                                </div>
                                <span className="text-[10px] text-slate-500 block mt-0.5">
                                  Agent:{" "}
                                  <span className="text-slate-300 font-medium">
                                    {step.step_name
                                      .replace(/_/g, " ")
                                      .replace(/\b\w/g, (c) => c.toUpperCase())}
                                  </span>
                                  {step.agent_id && (
                                    <span className="ml-2 font-mono text-slate-600 text-[9px]">
                                      [{step.agent_id.slice(0, 8)}]
                                    </span>
                                  )}
                                </span>
                                {step.error_message && (
                                  <span className="text-[10px] text-rose-450 bg-rose-500/5 p-2 border border-rose-900/30 rounded mt-1.5 block font-mono">
                                    Error: {step.error_message}
                                  </span>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

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

        {/* Workflow Inspector Panel */}
        <div id="workflow-inspector" className="lg:col-span-5 z-10">
          <div className="glass-card p-6 rounded-2xl space-y-6 sticky top-6">
            <div className="card-glow" />
            <div>
              <h3 className="font-bold text-slate-100 text-base">
                Workflow Inspector
              </h3>
              <p className="text-xs text-slate-450 mt-0.5">
                Enter a workflow ID to trace the exact agent step logs and
                execution times.
              </p>
            </div>

            <form onSubmit={handleInspect} className="flex gap-2 relative z-10">
              <input
                type="text"
                placeholder="Workflow ID..."
                value={inspectorId}
                onChange={(e) => setInspectorId(e.target.value)}
                className="flex-1 bg-[#0d1329]/80 border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 text-slate-200 transition-all"
              />
              <button
                type="submit"
                disabled={inspectLoading}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow transition-colors flex items-center gap-1.5 disabled:bg-indigo-500"
              >
                {inspectLoading && (
                  <RefreshCw className="w-3 h-3 animate-spin" />
                )}
                Trace
              </button>
            </form>

            {/* Trace Output */}
            {inspectLoading ? (
              <div className="text-center py-12 text-slate-500 text-xs">
                <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-slate-450" />
                Loading timeline...
              </div>
            ) : inspectedWf ? (
              <div className="space-y-6 border-t border-slate-800/40 pt-6 animate-fadeIn z-10 relative">
                {/* Meta details */}
                <div className="bg-[#0d1329]/50 p-4 rounded-xl border border-slate-800 space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-455">Workflow Type</span>
                    <span className="font-bold text-slate-200">
                      {inspectedWf.workflow_type}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-455">Status</span>
                    <span
                      className={`font-bold px-2 py-0.5 border rounded-full text-[8px] uppercase ${getStatusColor(inspectedWf.status)}`}
                    >
                      {inspectedWf.status}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-455">Ticket ID</span>
                    <span className="font-mono font-medium text-slate-400">
                      {inspectedWf.ticket_id}
                    </span>
                  </div>
                </div>

                {/* Timeline */}
                <div className="space-y-4">
                  <h4 className="text-xs font-bold text-slate-450 uppercase tracking-wider">
                    Execution Pipeline
                  </h4>
                  {inspectedSteps.length === 0 ? (
                    <div className="text-center py-6 text-slate-550 text-xs">
                      No step logs found.
                    </div>
                  ) : (
                    <div className="space-y-4 relative pl-5 border-l border-slate-800 ml-2">
                      {inspectedSteps.map((step, idx) => (
                        <div
                          key={step.id}
                          className="relative text-xs space-y-1"
                        >
                          <span
                            className={`absolute -left-[25px] top-1.5 w-2.5 h-2.5 rounded-full border border-[#0d1329] ring-4 ring-indigo-950/20 ${
                              step.status === "completed"
                                ? "bg-emerald-500"
                                : step.status === "running"
                                  ? "bg-blue-500 animate-pulse"
                                  : step.status === "failed"
                                    ? "bg-rose-500"
                                    : "bg-slate-500"
                            }`}
                          />
                          <div className="flex justify-between font-bold">
                            <span className="text-slate-300">
                              {idx + 1}. {step.step_name}
                            </span>
                            <span
                              className={`text-[8px] font-extrabold uppercase px-1.5 rounded ${
                                step.status === "completed"
                                  ? "text-emerald-450 bg-emerald-500/10 border border-emerald-500/20"
                                  : step.status === "running"
                                    ? "text-blue-450 bg-blue-500/10 border border-blue-500/20"
                                    : step.status === "failed"
                                      ? "text-rose-450 bg-rose-500/10 border border-rose-500/20"
                                      : "text-slate-400 bg-slate-500/10 border border-slate-500/20"
                              }`}
                            >
                              {step.status}
                            </span>
                          </div>

                          <div className="text-[10px] text-slate-500 font-medium">
                            Agent:{" "}
                            <span className="text-slate-300 font-semibold">
                              {step.step_name
                                .replace(/_/g, " ")
                                .replace(/\b\w/g, (c) => c.toUpperCase())}
                            </span>
                            {step.agent_id && (
                              <span className="ml-2 font-mono text-slate-600 text-[9px]">
                                [{step.agent_id.slice(0, 8)}]
                              </span>
                            )}
                          </div>

                          {(step.started_at || step.completed_at) && (
                            <div className="text-[9px] text-slate-500 font-mono space-y-0.5 bg-[#090d1f]/40 p-2 rounded border border-slate-800/40 mt-1">
                              {step.started_at && (
                                <div>Start: {step.started_at}</div>
                              )}
                              {step.completed_at && (
                                <div>Stop: {step.completed_at}</div>
                              )}
                            </div>
                          )}

                          {step.error_message && (
                            <div className="text-[9px] text-rose-450 bg-rose-500/5 border border-rose-900/30 p-2.5 rounded font-mono mt-1">
                              Error: {step.error_message}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="border border-dashed border-slate-800 rounded-2xl p-12 text-center text-slate-500 text-xs">
                <Cpu className="w-8 h-8 mx-auto mb-2 text-slate-600 animate-pulse" />
                No workflow traced. Choose "Inspect Steps" on any active
                execution or enter an ID above.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
