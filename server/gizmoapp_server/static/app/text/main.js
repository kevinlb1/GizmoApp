import { fetchBootstrap } from "../api.js";
import { setupInstallControls } from "../install.js";


function readConfig() {
  const raw = document.getElementById("gizmoapp-config");
  return JSON.parse(raw.textContent);
}


function setText(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = value;
  }
}


function updateHealthPill(healthy) {
  const pill = document.getElementById("text-health-pill");
  if (!pill) {
    return;
  }
  pill.dataset.state = healthy ? "healthy" : "degraded";
  pill.textContent = healthy ? "Ready" : "Offline";
}


function registerServiceWorker(url) {
  if (!("serviceWorker" in navigator) || !window.isSecureContext) {
    return;
  }

  window.addEventListener("load", () => {
    navigator.serviceWorker.register(url).catch((error) => {
      console.warn("Service worker registration failed", error);
    });
  });
}


async function bootstrap() {
  const config = readConfig();
  setupInstallControls({
    button: document.getElementById("install-button"),
    hint: document.getElementById("install-hint"),
    appName: config.appName,
  });
  registerServiceWorker(config.serviceWorkerUrl);

  setText("prefix-value", config.urlPrefix || "/");
  setText("location-value", config.defaultLocation?.label || "UBC Vancouver");

  try {
    const payload = await fetchBootstrap(config.apiBase);
    setText("mode-value", payload.app.mode);
    setText("shell-value", payload.app.shellLabel);
    setText("db-value", payload.health.database);
    setText("location-value", payload.capabilitySummary?.defaultLocation?.label || "UBC Vancouver");
    updateHealthPill(payload.health.status === "ok");
  } catch (error) {
    console.error(error);
    setText("db-value", "Unknown");
    updateHealthPill(false);
  }
}


bootstrap();
