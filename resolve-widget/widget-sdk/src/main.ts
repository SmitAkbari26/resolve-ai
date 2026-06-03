(async function () {
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
      console.warn("ResolveAI Widget blocked:", validation.message);

      return;
    }

    // ============================
    // Load Config
    // ============================

    const configResponse = await fetch(
      `http://localhost:8000/api/v1/widget-configurations/by-api-key/${apiKey}`,
    );

    if (!configResponse.ok) {
      throw new Error("Failed to load widget configuration");
    }

    const config = await configResponse.json();

    (window as any).__RESOLVE_WIDGET_CONFIG__ = {
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
    };

    // ============================
    // Mount Widget
    // ============================

    const root = document.createElement("div");

    root.id = "resolve-widget-root";

    document.body.appendChild(root);

    const script = document.createElement("script");

    script.type = "module";

    script.src = "http://localhost:5173/src/main.tsx";

    document.body.appendChild(script);
  } catch (error) {
    console.error("ResolveAI Widget Error", error);
  }
})();

export {};
