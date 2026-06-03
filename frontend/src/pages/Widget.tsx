import { useEffect, useState } from "react";
import { Layout, RefreshCw, Building2 } from "lucide-react";

import ColorPicker from "../components/ColorPicker";
import PositionSelector from "../components/PositionSelector";
import WidgetSettings from "../components/WidgetSettings";
import LivePreview from "../components/LivePreview";
import AppearanceControls from "../components/AppearanceControls";
import BehaviorControls from "../components/BehaviorControls";
import ThemePresets from "../components/ThemePresets";

import {
  tenantApi,
  widgetConfigurationApi,
  type Tenant,
} from "../services/api";

export default function Widget() {
  const [saving, setSaving] = useState(false);

  const [tenants, setTenants] = useState<Tenant[]>([]);

  const [selectedTenantId, setSelectedTenantId] = useState("");

  const [config, setConfig] = useState({
    primaryColor: "#8b5cf6",
    position: "right",

    companyName: "Nova Electronics",

    welcomeMessage: "Welcome to Nova Support 👋",

    width: 430,
    height: 720,

    borderRadius: 32,
    launcherSize: 64,

    showBadge: true,

    fullscreenMobile: true,

    autoOpen: false,
    autoOpenDelay: 2000,
  });

  useEffect(() => {
    loadTenants();
  }, []);

  useEffect(() => {
    if (!selectedTenantId) return;

    loadConfiguration(selectedTenantId);
  }, [selectedTenantId]);

  const loadTenants = async () => {
    try {
      const result = await tenantApi.listTenants();

      setTenants(result);

      if (result && result.length > 0) {
        setSelectedTenantId(result[0].id);
      }
    } catch (error) {
      console.error(error);
    }
  };

  const loadConfiguration = async (tenantId: string) => {
    try {
      const result = await widgetConfigurationApi.get(tenantId);

      setConfig({
        primaryColor: result.primary_color,

        position: result.position,

        companyName: result.company_name,

        welcomeMessage: result.welcome_message,

        width: result.width,
        height: result.height,

        borderRadius: result.border_radius,

        launcherSize: result.launcher_size,

        showBadge: result.show_badge,

        fullscreenMobile: result.fullscreen_mobile,

        autoOpen: result.auto_open,

        autoOpenDelay: result.auto_open_delay,
      });
    } catch (error) {
      console.error(error);
    }
  };

  const applyChanges = async () => {
    try {
      setSaving(true);

      await widgetConfigurationApi.save(selectedTenantId, {
        primary_color: config.primaryColor,

        position: config.position,

        company_name: config.companyName,

        welcome_message: config.welcomeMessage,

        width: config.width,
        height: config.height,

        border_radius: config.borderRadius,

        launcher_size: config.launcherSize,

        show_badge: config.showBadge,

        fullscreen_mobile: config.fullscreenMobile,

        auto_open: config.autoOpen,

        auto_open_delay: config.autoOpenDelay,
      });

      const iframe = document.getElementById(
        "preview-frame",
      ) as HTMLIFrameElement;

      iframe?.contentWindow?.postMessage(
        {
          type: "UPDATE_WIDGET_CONFIG",
          payload: config,
        },
        "*",
      );
    } catch (error) {
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="h-[calc(100vh-100px)] flex overflow-hidden rounded-3xl border border-slate-800 bg-slate-950">
      {/* Sidebar */}
      <aside className="w-[460px] border-r border-slate-800 bg-slate-900 overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 z-20 bg-slate-900 border-b border-slate-800 p-6">
          <div className="flex items-center gap-4">
            <div className="h-14 w-14 rounded-3xl bg-emerald-500/15 flex items-center justify-center">
              <Layout className="w-7 h-7 text-emerald-400" />
            </div>

            <div>
              <h1 className="text-2xl font-bold text-white">Widget Builder</h1>

              <p className="text-slate-400 text-sm">
                Configure your AI assistant
              </p>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5">
          {/* Tenant */}
          <div className="glass-card p-5 rounded-3xl">
            <div className="flex items-center gap-2 mb-4">
              <Building2 className="w-5 h-5 text-emerald-400" />

              <h2 className="font-semibold">Tenant</h2>
            </div>

            <select
              value={selectedTenantId}
              onChange={(e) => setSelectedTenantId(e.target.value)}
              className="
                w-full
                bg-slate-950
                border
                border-slate-700
                rounded-2xl
                p-3
                outline-none
              "
            >
              {tenants.map((tenant) => (
                <option key={tenant.id} value={tenant.id}>
                  {tenant.name}
                </option>
              ))}
            </select>
          </div>

          <div className="glass-card p-5 rounded-3xl">
            <WidgetSettings
              companyName={config.companyName}
              welcomeMessage={config.welcomeMessage}
              onCompanyChange={(companyName) =>
                setConfig({
                  ...config,
                  companyName,
                })
              }
              onWelcomeChange={(welcomeMessage) =>
                setConfig({
                  ...config,
                  welcomeMessage,
                })
              }
            />
          </div>

          <div className="glass-card p-5 rounded-3xl">
            <ColorPicker
              value={config.primaryColor}
              onChange={(primaryColor) =>
                setConfig({
                  ...config,
                  primaryColor,
                })
              }
            />
          </div>

          <div className="glass-card p-5 rounded-3xl">
            <PositionSelector
              value={config.position}
              onChange={(position) =>
                setConfig({
                  ...config,
                  position,
                })
              }
            />
          </div>

          <div className="glass-card p-5 rounded-3xl">
            <AppearanceControls config={config} setConfig={setConfig} />
          </div>

          <div className="glass-card p-5 rounded-3xl">
            <BehaviorControls config={config} setConfig={setConfig} />
          </div>

          <div className="glass-card p-5 rounded-3xl">
            <ThemePresets config={config} setConfig={setConfig} />
          </div>

          <button
            onClick={applyChanges}
            disabled={saving}
            className="
              w-full
              flex
              items-center
              justify-center
              gap-3
              py-4
              rounded-2xl
              font-semibold
              transition-all
              hover:scale-[1.02]
              shadow-xl
            "
            style={{
              backgroundColor: config.primaryColor,
            }}
          >
            <RefreshCw className={`w-5 h-5 ${saving ? "animate-spin" : ""}`} />

            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </aside>

      {/* Preview */}
      <div className="flex-1 p-8 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <div className="h-full rounded-[40px] border border-slate-700 bg-slate-900 shadow-2xl overflow-hidden">
          <div className="h-12 border-b border-slate-700 flex items-center px-4 gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <div className="w-3 h-3 rounded-full bg-green-500" />
          </div>

          <LivePreview />
        </div>
      </div>
    </div>
  );
}
