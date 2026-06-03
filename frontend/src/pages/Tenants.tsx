import { useEffect, useState } from "react";

import {
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Plus,
  Trash2,
  Copy,
  Globe,
} from "lucide-react";

import { tenantApi, type Tenant } from "../services/api";

import { widgetDomainApi, type WidgetDomain } from "../services/api";

export default function Tenants() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedTenantId, setExpandedTenantId] = useState<string | null>(null);
  const [domains, setDomains] = useState<Record<string, WidgetDomain[]>>({});
  const [newDomain, setNewDomain] = useState("");
  const [newTenant, setNewTenant] = useState({
    name: "",
    slug: "",
  });

  const loadTenants = async () => {
    try {
      setLoading(true);

      const data = await tenantApi.listTenants();

      setTenants(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTenants();
  }, []);

  const expandTenant = async (tenantId: string) => {
    if (expandedTenantId === tenantId) {
      setExpandedTenantId(null);
      return;
    }

    setExpandedTenantId(tenantId);

    const tenantDomains = await widgetDomainApi.getDomains(tenantId);

    setDomains((prev) => ({
      ...prev,
      [tenantId]: tenantDomains,
    }));
  };

  const addDomain = async (tenantId: string) => {
    if (!newDomain.trim()) return;

    await widgetDomainApi.createDomain(tenantId, newDomain);

    const tenantDomains = await widgetDomainApi.getDomains(tenantId);

    setDomains((prev) => ({
      ...prev,
      [tenantId]: tenantDomains,
    }));

    setNewDomain("");
  };

  const deleteDomain = async (tenantId: string, domainId: string) => {
    await widgetDomainApi.deleteDomain(domainId);

    const tenantDomains = await widgetDomainApi.getDomains(tenantId);

    setDomains((prev) => ({
      ...prev,
      [tenantId]: tenantDomains,
    }));
  };

  const createTenant = async () => {
    await tenantApi.createTenant(newTenant);

    setNewTenant({
      name: "",
      slug: "",
    });

    loadTenants();
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">
            Tenant Management
          </h1>

          <p className="text-slate-400 mt-1">
            Manage customers, API keys and domains.
          </p>
        </div>

        <button
          onClick={loadTenants}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      <div className="glass-card p-6 rounded-2xl space-y-4">
        <h2 className="font-semibold">Create Tenant</h2>

        <input
          value={newTenant.name}
          placeholder="Company Name"
          onChange={(e) =>
            setNewTenant({
              ...newTenant,
              name: e.target.value,
            })
          }
          className="w-full p-3 rounded-xl bg-slate-900"
        />

        <input
          value={newTenant.slug}
          placeholder="Slug"
          onChange={(e) =>
            setNewTenant({
              ...newTenant,
              slug: e.target.value,
            })
          }
          className="w-full p-3 rounded-xl bg-slate-900"
        />

        <button
          onClick={createTenant}
          className="bg-emerald-600 px-4 py-3 rounded-xl flex items-center gap-2"
        >
          <Plus size={16} />
          Create Tenant
        </button>
      </div>

      {tenants.map((tenant) => {
        const isExpanded = expandedTenantId === tenant.id;

        return (
          <div
            key={tenant.id}
            className="glass-card rounded-2xl overflow-hidden"
          >
            <div
              onClick={() => expandTenant(tenant.id)}
              className="p-5 cursor-pointer flex justify-between items-center"
            >
              <div>
                <h3 className="font-semibold text-lg">{tenant.name}</h3>

                <p className="text-sm text-slate-500">{tenant.slug}</p>
              </div>

              {isExpanded ? <ChevronUp /> : <ChevronDown />}
            </div>

            {isExpanded && (
              <div className="border-t border-slate-800 p-6 space-y-6">
                <div>
                  <label className="text-xs text-slate-400">API Key</label>

                  <div className="flex gap-2 mt-2">
                    <input
                      value={tenant.api_key}
                      readOnly
                      className="flex-1 p-3 rounded-xl bg-slate-900"
                    />

                    <button
                      onClick={() =>
                        navigator.clipboard.writeText(tenant.api_key)
                      }
                      className="px-4 rounded-xl bg-slate-800"
                    >
                      <Copy size={16} />
                    </button>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold flex items-center gap-2">
                    <Globe size={16} />
                    Domains
                  </h4>

                  <div className="space-y-2 mt-4">
                    {(domains[tenant.id] || []).map((domain) => (
                      <div
                        key={domain.id}
                        className="flex justify-between items-center bg-slate-900 p-3 rounded-xl"
                      >
                        <span>{domain.domain}</span>

                        <button
                          onClick={() => deleteDomain(tenant.id, domain.id)}
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    ))}
                  </div>

                  <div className="flex gap-2 mt-4">
                    <input
                      value={newDomain}
                      placeholder="example.com"
                      onChange={(e) => setNewDomain(e.target.value)}
                      className="flex-1 p-3 rounded-xl bg-slate-900"
                    />

                    <button
                      onClick={() => addDomain(tenant.id)}
                      className="bg-indigo-600 px-4 rounded-xl"
                    >
                      Add
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
