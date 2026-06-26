import { fetchBootstrap } from "./api.js";
import { setupInstallControls } from "./install.js";
import { SceneRenderer } from "./scene.js";


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
  const pill = document.getElementById("health-pill");
  if (!pill) {
    return;
  }
  const label = healthy ? "Status: ready" : "Status: offline";
  pill.dataset.state = healthy ? "healthy" : "degraded";
  pill.setAttribute("aria-label", label);
  pill.title = healthy ? "Ready" : "Offline";
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
  const renderer = new SceneRenderer(document.getElementById("scene-canvas"));

  setupInstallControls({
    button: document.getElementById("install-button"),
    hint: document.getElementById("install-hint"),
    appName: config.appName,
  });
  registerServiceWorker(config.serviceWorkerUrl);

  try {
    const payload = await fetchBootstrap(config.apiBase);
    setText("mode-value", payload.app.mode);
    setText("shell-value", payload.app.shellLabel);
    setText("api-value", "Online");
    renderer.setNodes([]);
    updateHealthPill(payload.health.status === "ok");
  } catch (error) {
    console.error(error);
    setText("api-value", "Error");
    updateHealthPill(false);
  }
}


bootstrap();
