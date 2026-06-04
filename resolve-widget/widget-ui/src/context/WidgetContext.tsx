import { createContext, useContext, useState, useEffect } from "react";

export interface WidgetConfig {
  primaryColor: string;
  position: string;
  companyName: string;
  welcomeMessage: string;
  width: number;
  height: number;
  borderRadius: number;
  launcherSize: number;
  showBadge: boolean;
  fullscreenMobile: boolean;
  autoOpen: boolean;
  autoOpenDelay: number;
}

export const defaultConfig: WidgetConfig = {
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
};

const WidgetContext = createContext<WidgetConfig>(defaultConfig);

export const useWidgetConfig = () => useContext(WidgetContext);

/**
 * Stateful provider that:
 * 1. Accepts an initial config from bootstrap
 * 2. Listens for postMessage({ type: "UPDATE_WIDGET_CONFIG", payload }) from the
 *    admin Widget Builder and live-updates all consumers immediately.
 */
export function WidgetProvider({
  value,
  children,
}: {
  value: WidgetConfig;
  children: React.ReactNode;
}) {
  const [config, setConfig] = useState<WidgetConfig>(value);

  // Sync if parent re-mounts with a different initial value
  useEffect(() => {
    setConfig(value);
  }, [value]);

  // Listen for live config updates posted by the admin Widget Builder iframe
  useEffect(() => {
    const handler = (event: MessageEvent) => {
      if (event.data?.type === "UPDATE_WIDGET_CONFIG") {
        const p = event.data.payload;
        setConfig((prev) => ({
          ...prev,
          primaryColor:    p.primaryColor    ?? prev.primaryColor,
          position:        p.position        ?? prev.position,
          companyName:     p.companyName     ?? prev.companyName,
          welcomeMessage:  p.welcomeMessage  ?? prev.welcomeMessage,
          width:           p.width           ?? prev.width,
          height:          p.height          ?? prev.height,
          borderRadius:    p.borderRadius    ?? prev.borderRadius,
          launcherSize:    p.launcherSize    ?? prev.launcherSize,
          showBadge:       p.showBadge       ?? prev.showBadge,
          fullscreenMobile: p.fullscreenMobile ?? prev.fullscreenMobile,
          autoOpen:        p.autoOpen        ?? prev.autoOpen,
          autoOpenDelay:   p.autoOpenDelay   ?? prev.autoOpenDelay,
        }));
      }
    };

    window.addEventListener("message", handler);
    return () => window.removeEventListener("message", handler);
  }, []);

  return (
    <WidgetContext.Provider value={config}>
      {children}
    </WidgetContext.Provider>
  );
}

