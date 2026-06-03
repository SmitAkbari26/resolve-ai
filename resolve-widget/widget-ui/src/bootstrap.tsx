import ReactDOM from "react-dom/client";

import App from "./App";
import { WidgetProvider } from "./context/WidgetContext";

export async function bootstrapWidget() {
  if (document.getElementById("resolve-widget-root")) {
    return;
  }

  const globalConfig = (window as any).ResolveAIConfig;

  if (!globalConfig?.apiKey) {
    console.error("ResolveAI: apiKey is required");
    return;
  }

  const apiKey = globalConfig.apiKey;

  try {
    // ============================
    // Validate Domain
    // ============================

    const validateResponse = await fetch(
      "http://localhost:8000/api/v1/widget-domains/validate",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          api_key: apiKey,
          domain: window.location.hostname,
        }),
      },
    );

    if (!validateResponse.ok) {
      throw new Error("Failed to validate domain");
    }

    const validation = await validateResponse.json();

    if (!validation.valid) {
      console.warn("ResolveAI Widget Blocked:", validation.message);

      return;
    }

    // ============================
    // Load Configuration
    // ============================

    const configResponse = await fetch(
      `http://localhost:8000/api/v1/widget-configurations/by-api-key/${apiKey}`,
    );

    if (!configResponse.ok) {
      throw new Error("Failed to load widget configuration");
    }

    const config = await configResponse.json();

    // ============================
    // Create Root
    // ============================

    const rootElement = document.createElement("div");

    rootElement.id = "resolve-widget-root";

    document.body.appendChild(rootElement);

    // ============================
    // Render Widget
    // ============================

    const root = ReactDOM.createRoot(rootElement);

    root.render(
      <WidgetProvider
        value={{
          primaryColor: config.primary_color,
          position: config.position,
          companyName: config.company_name,
          welcomeMessage: config.welcome_message,
          width: config.width,
          height: config.height,
          borderRadius: config.border_radius,
          launcherSize: config.launcher_size,
          showBadge: config.show_badge,
          fullscreenMobile: config.fullscreen_mobile,
          autoOpen: config.auto_open,
          autoOpenDelay: config.auto_open_delay,
        }}
      >
        <App />
      </WidgetProvider>,
    );
  } catch (error) {
    console.error("ResolveAI Widget Error", error);
  }
}
