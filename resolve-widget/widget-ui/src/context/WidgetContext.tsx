import { createContext, useContext } from "react";

export interface WidgetConfig {
  primaryColor: string;
  position: string;
  companyName: string;
  welcomeMessage: string;
  width: 430;
  height: 720;
  borderRadius: 32;
  launcherSize: 64;
  showBadge: true;
  fullscreenMobile: true;
  autoOpen: false;
  autoOpenDelay: 2000;
}

const defaultConfig: WidgetConfig = {
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

const WidgetContext = createContext(defaultConfig);

export const WidgetProvider = WidgetContext.Provider;

export const useWidgetConfig = () => useContext(WidgetContext);
