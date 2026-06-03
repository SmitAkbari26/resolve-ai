import React, { useState, useEffect } from 'react';
import { approvalApi } from '../services/api';
import { 
  Check, 
  X, 
  RefreshCw, 
  ShieldAlert, 
  AlertCircle, 
  CheckCircle2, 
  ClipboardCheck,
  DollarSign
} from 'lucide-react';

interface Approval {
  id: string;
  ticket_id: string;
  approval_type: string;
  reason: string;
  amount?: number | null;
  status: string;
  requested_by: string;
  created_at: string;
  severity?: string;
}

export const Approvals: React.FC = () => {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actioningId, setActioningId] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const fetchApprovals = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await approvalApi.listApprovals('pending');
      setApprovals(Array.isArray(data) ? data : (data?.data ?? []));
    } catch (err: any) {
      setError('Failed to fetch pending approvals. Verify backend service status.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, []);

  const handleDecision = async (approvalId: string, decision: 'approved' | 'rejected') => {
    setActioningId(approvalId);
    setError(null);
    setSuccessMsg(null);
    try {
      await approvalApi.updateApproval(approvalId, { status: decision });
      setSuccessMsg(`Approval ${approvalId} has been successfully ${decision}`);
      setTimeout(() => setSuccessMsg(null), 3000);
      fetchApprovals();
    } catch (err: any) {
      setError(`Failed to process ${decision} action on approval ${approvalId}`);
    } finally {
      setActioningId(null);
    }
  };

  const pendingCount = approvals.length;
  const highSeverityCount = approvals.filter(x => x.severity === 'high').length;
  const totalPaused = approvals.filter(x => x.status === 'pending').length;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Approval Center</h1>
          <p className="text-sm text-slate-400 mt-1">Review, authorize, or reject automated workflow escalations and refund triggers.</p>
        </div>
        <button
          onClick={fetchApprovals}
          className="flex items-center gap-2 px-4 py-2 border border-slate-800 bg-[#090d1f]/40 hover:bg-[#090d1f]/80 text-slate-200 text-xs font-semibold rounded-xl transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Stats Widgets */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        {[
          { label: 'Pending Approvals', value: pendingCount, color: 'text-amber-400' },
          { label: 'High Severity', value: highSeverityCount, color: 'text-rose-400' },
          { label: 'Paused Workflows', value: totalPaused, color: 'text-indigo-400' }
        ].map((stat, i) => (
          <div key={i} className="glass-card p-5 rounded-2xl">
            <div className="card-glow" />
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">{stat.label}</span>
            <span className={`text-2xl font-bold mt-1 block ${stat.color}`}>{stat.value}</span>
          </div>
        ))}
      </div>

      {/* Alerts */}
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

      {/* Approval Cards */}
      {loading ? (
        <div className="text-center py-12 text-slate-500 text-sm">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-slate-600" />
          Loading approvals...
        </div>
      ) : approvals.length === 0 ? (
        <div className="glass-card rounded-2xl p-12 text-center text-slate-500">
          <div className="card-glow" />
          <ClipboardCheck className="w-8 h-8 mx-auto mb-3 text-slate-600" />
          No pending approvals found. All workflows are clear!
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {approvals.map((approval) => (
            <div key={approval.id} className="glass-card rounded-2xl overflow-hidden flex flex-col hover:border-amber-500/30 transition-all duration-300">
              <div className="card-glow" />
              {/* Header */}
              <div className="p-5 border-b border-slate-800/40 flex items-center justify-between z-10">
                <div className="space-y-0.5">
                  <h3 className="font-bold text-slate-200 text-sm">{approval.approval_type || 'General Approval'}</h3>
                  <span className="text-[10px] font-mono text-slate-500 block">ID: {approval.id}</span>
                </div>
                <span className="text-[9px] font-extrabold uppercase tracking-wider px-2 py-0.5 bg-amber-500/10 border border-amber-500/20 text-amber-400 rounded-full">
                  {approval.status}
                </span>
              </div>

              {/* Body */}
              <div className="p-5 flex-1 space-y-3.5 text-xs text-slate-400 z-10">
                <div className="grid grid-cols-2 gap-3 pb-3 border-b border-slate-800/30">
                  <div>
                    <span className="text-slate-500 block mb-0.5">Ticket ID</span>
                    <span className="font-mono text-slate-300 font-medium">{approval.ticket_id}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block mb-0.5">Requested By</span>
                    <span className="font-medium text-slate-300">{approval.requested_by}</span>
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-slate-500 block">Escalation Reason</span>
                  <p className="bg-[#0d1329]/50 p-3 rounded-xl border border-slate-800 text-slate-300 italic">
                    "{approval.reason}"
                  </p>
                </div>

                {approval.amount !== undefined && approval.amount !== null && (
                  <div className="flex items-center gap-1.5 bg-amber-500/5 text-amber-300 p-2.5 rounded-xl border border-amber-500/15">
                    <DollarSign className="w-4 h-4 text-amber-500 shrink-0" />
                    <span className="font-semibold">Refund Amount: ${approval.amount}</span>
                  </div>
                )}

                <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1">
                  <span>Created: {approval.created_at}</span>
                  {approval.severity === 'high' && (
                    <span className="flex items-center gap-1 text-rose-400 font-semibold bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                      <ShieldAlert className="w-3 h-3" /> High Severity
                    </span>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="p-4 border-t border-slate-800/30 grid grid-cols-2 gap-3 z-10">
                <button
                  disabled={actioningId !== null}
                  onClick={() => handleDecision(approval.id, 'approved')}
                  className="flex items-center justify-center gap-1.5 py-2.5 px-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow transition-colors disabled:bg-emerald-900 disabled:text-emerald-600"
                >
                  {actioningId === approval.id ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Check className="w-3.5 h-3.5" />
                  )}
                  Approve
                </button>

                <button
                  disabled={actioningId !== null}
                  onClick={() => handleDecision(approval.id, 'rejected')}
                  className="flex items-center justify-center gap-1.5 py-2.5 px-3 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-xl text-xs font-bold transition-colors disabled:opacity-50"
                >
                  {actioningId === approval.id ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <X className="w-3.5 h-3.5" />
                  )}
                  Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
