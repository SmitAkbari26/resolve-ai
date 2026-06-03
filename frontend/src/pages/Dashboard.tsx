import React from 'react';
import { 
  Ticket, 
  Percent, 
  AlertTriangle, 
  Clock, 
  Activity, 
  CheckCircle2, 
  Cpu, 
  Database 
} from 'lucide-react';

export const Dashboard: React.FC = () => {
  const metrics = {
    active_tickets: 148,
    ai_resolution_rate: 82,
    escalations: 17,
    pending_approvals: 9,
  };

  const workflows = [
    {
      workflow_id: 'WF-1001',
      current_step: 'conversation_analysis',
      status: 'running',
    },
    {
      workflow_id: 'WF-1002',
      current_step: 'approval_pending',
      status: 'paused',
    },
    {
      workflow_id: 'WF-1003',
      current_step: 'notification_dispatch',
      status: 'running',
    },
  ];

  const agents = [
    {
      name: 'Conversation Agent',
      status: 'active',
      avg_latency_ms: 124,
    },
    {
      name: 'Decision Agent',
      status: 'active',
      avg_latency_ms: 96,
    },
    {
      name: 'Approval Agent',
      status: 'active',
      avg_latency_ms: 141,
    },
  ];

  const systemComponents = [
    {
      name: 'PostgreSQL Database',
      status: 'healthy',
      icon: Database
    },
    {
      name: 'Redis Cache Store',
      status: 'healthy',
      icon: Activity
    },
    {
      name: 'LLM Gateway Client',
      status: 'healthy',
      icon: Cpu
    },
    {
      name: 'Notification Service',
      status: 'healthy',
      icon: CheckCircle2
    },
  ];

  return (
    <div className="space-y-8 animate-fadeIn text-slate-100">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">System Dashboard</h1>
        <p className="text-sm text-slate-400 mt-1">Real-time telemetry, agent metrics, and live executions.</p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Active Tickets */}
        <div className="glass-card p-6 rounded-2xl flex items-center justify-between group hover:border-blue-500/50 transition-all duration-300">
          <div className="card-glow" />
          <div className="z-10">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Active Tickets</span>
            <span className="text-3xl font-bold text-slate-100 mt-1.5 block">{metrics.active_tickets}</span>
          </div>
          <div className="bg-blue-500/10 text-blue-400 p-3 rounded-xl border border-blue-500/20 group-hover:bg-blue-500 group-hover:text-white transition-all duration-305 z-10">
            <Ticket className="w-5 h-5" />
          </div>
        </div>

        {/* Resolution Rate */}
        <div className="glass-card p-6 rounded-2xl flex items-center justify-between group hover:border-emerald-500/50 transition-all duration-300">
          <div className="card-glow" />
          <div className="z-10">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">AI Resolution Rate</span>
            <span className="text-3xl font-bold text-slate-100 mt-1.5 block">{metrics.ai_resolution_rate}%</span>
          </div>
          <div className="bg-emerald-500/10 text-emerald-450 p-3 rounded-xl border border-emerald-500/20 group-hover:bg-emerald-500 group-hover:text-white transition-all duration-305 z-10">
            <Percent className="w-5 h-5" />
          </div>
        </div>

        {/* Escalations */}
        <div className="glass-card p-6 rounded-2xl flex items-center justify-between group hover:border-amber-500/50 transition-all duration-300">
          <div className="card-glow" />
          <div className="z-10">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Escalations</span>
            <span className="text-3xl font-bold text-slate-100 mt-1.5 block">{metrics.escalations}</span>
          </div>
          <div className="bg-amber-500/10 text-amber-400 p-3 rounded-xl border border-amber-500/20 group-hover:bg-amber-500 group-hover:text-white transition-all duration-305 z-10">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>

        {/* Pending Approvals */}
        <div className="glass-card p-6 rounded-2xl flex items-center justify-between group hover:border-purple-500/50 transition-all duration-300">
          <div className="card-glow" />
          <div className="z-10">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Pending Approvals</span>
            <span className="text-3xl font-bold text-slate-100 mt-1.5 block">{metrics.pending_approvals}</span>
          </div>
          <div className="bg-purple-500/10 text-purple-400 p-3 rounded-xl border border-purple-500/20 group-hover:bg-purple-500 group-hover:text-white transition-all duration-305 z-10">
            <Clock className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Main grids */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live Workflows */}
        <div className="glass-card p-6 rounded-2xl lg:col-span-2 space-y-5">
          <div className="card-glow" />
          <div className="flex items-center justify-between border-b border-slate-800/40 pb-3 z-10 relative">
            <h3 className="font-bold text-slate-200 text-base">Live Workflows</h3>
            <span className="text-[9px] font-bold uppercase tracking-wider px-2.5 py-0.5 bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-full">Orchestration</span>
          </div>
          <div className="divide-y divide-slate-800/30 z-10 relative">
            {workflows.map((wf) => (
              <div key={wf.workflow_id} className="py-4 flex items-center justify-between group">
                <div className="flex items-center gap-3">
                  <span className={`w-2 h-2 rounded-full ${wf.status === 'paused' ? 'bg-amber-400 animate-pulse' : 'bg-blue-500 animate-pulse'}`} />
                  <div>
                    <span className="font-semibold text-sm text-slate-200 block">{wf.workflow_id}</span>
                    <span className="text-xs text-slate-450 capitalize">{wf.current_step.replace(/_/g, ' ')}</span>
                  </div>
                </div>
                <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full capitalize ${
                  wf.status === 'paused' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-blue-500/10 text-blue-450 border border-blue-500/20'
                }`}>
                  {wf.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Pipeline & System Health */}
        <div className="space-y-6">
          {/* Agent health */}
          <div className="glass-card p-6 rounded-2xl space-y-4">
            <div className="card-glow" />
            <h3 className="font-bold text-slate-200 text-sm border-b border-slate-800/40 pb-2 z-10 relative">Agent Health</h3>
            <div className="space-y-3 z-10 relative">
              {agents.map((agent) => (
                <div key={agent.name} className="flex items-center justify-between text-xs py-1">
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    <span className="font-medium text-slate-300">{agent.name}</span>
                  </div>
                  <span className="font-mono text-slate-500">{agent.avg_latency_ms}ms</span>
                </div>
              ))}
            </div>
          </div>

          {/* System components */}
          <div className="glass-card p-6 rounded-2xl space-y-4">
            <div className="card-glow" />
            <h3 className="font-bold text-slate-200 text-sm border-b border-slate-800/40 pb-2 z-10 relative">System Components</h3>
            <div className="space-y-3 z-10 relative">
              {systemComponents.map((comp) => {
                const Icon = comp.icon;
                return (
                  <div key={comp.name} className="flex items-center justify-between text-xs py-1">
                    <div className="flex items-center gap-2.5 text-slate-305">
                      <Icon className="w-3.5 h-3.5 text-slate-500" />
                      <span className="font-medium">{comp.name}</span>
                    </div>
                    <span className="font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 capitalize">
                      {comp.status}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
