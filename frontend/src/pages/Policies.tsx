import React, { useEffect, useState } from "react";
import { policyApi } from "../services/api";
import {
  ShieldCheck,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  FileCheck,
  Layers,
} from "lucide-react";

interface Policy {
  id: string;
  title: string;
  category: string;
  version: number;
  active: boolean;
}

export const Policies: React.FC = () => {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [activeOnly, setActiveOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);

  const ITEMS_PER_PAGE = 6;

  const load = async () => {
    setLoading(true);

    try {
      const data = activeOnly
        ? await policyApi.listActivePolicies()
        : await policyApi.listPolicies();

      setPolicies(Array.isArray(data) ? data : []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setPage(1);
    load();
  }, [activeOnly]);

  const totalPages = Math.ceil(policies.length / ITEMS_PER_PAGE);

  const paginatedPolicies = policies.slice(
    (page - 1) * ITEMS_PER_PAGE,
    page * ITEMS_PER_PAGE,
  );

  const activeCount = policies.filter((p) => p.active).length;
  const inactiveCount = policies.filter((p) => !p.active).length;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-3">
            <ShieldCheck className="w-7 h-7 text-emerald-400" />
            Policies
          </h1>
          <p className="text-slate-400 mt-1">
            Review automation policy definitions
          </p>
        </div>

        <div className="flex gap-3 items-center">
          <label className="flex items-center gap-2 text-slate-300 text-sm bg-slate-900 border border-slate-800 px-4 py-3 rounded-2xl">
            <input
              type="checkbox"
              checked={activeOnly}
              onChange={(e) => setActiveOnly(e.target.checked)}
              className="accent-emerald-500"
            />
            Active Only
          </label>

          <button
            onClick={load}
            className="flex items-center gap-2 px-4 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-2xl text-slate-200 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {[
          { label: "Total Policies", value: policies.length, icon: Layers },
          { label: "Active", value: activeCount, icon: ShieldCheck },
          { label: "Inactive", value: inactiveCount, icon: FileCheck },
        ].map((stat, i) => (
          <div
            key={i}
            className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6 hover:border-emerald-500 transition-all"
          >
            <stat.icon className="w-6 h-6 text-emerald-400 mb-3" />
            <p className="text-slate-400 text-sm">{stat.label}</p>
            <h3 className="text-3xl font-bold text-white mt-2">{stat.value}</h3>
          </div>
        ))}
      </div>

      {/* Policy Cards */}
      {loading ? (
        <div className="grid gap-5">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="h-40 bg-slate-900 border border-slate-800 rounded-3xl animate-pulse"
            />
          ))}
        </div>
      ) : paginatedPolicies.length > 0 ? (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
          {paginatedPolicies.map((p) => (
            <div
              key={p.id}
              className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6 hover:border-emerald-500 transition-all duration-300"
            >
              <div className="flex justify-between items-start mb-5">
                <div>
                  <h3 className="font-semibold text-slate-100">{p.title}</h3>
                  <p className="text-xs text-slate-500 font-mono">{p.id}</p>
                </div>

                <span
                  className={`px-3 py-1 rounded-xl text-xs border ${
                    p.active
                      ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                      : "bg-slate-700/30 text-slate-400 border-slate-600"
                  }`}
                >
                  {p.active ? "Active" : "Inactive"}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-5">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
                  <p className="text-xs text-slate-500 mb-1">Category</p>
                  <p className="text-slate-200">{p.category}</p>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
                  <p className="text-xs text-slate-500 mb-1">Version</p>
                  <p className="text-slate-200">v{p.version}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-12 text-center text-slate-500">
          No policies found.
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
