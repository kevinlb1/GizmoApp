import { fetchBootstrap } from "./api.js";
import { setupInstallControls } from "./install.js";
import { SceneRenderer } from "./scene.js";


function readConfig() {
  const raw = document.getElementById("emmie-config");
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
  pill.dataset.state = healthy ? "healthy" : "degraded";
  pill.textContent = healthy ? "Healthy" : "Degraded";
}


function renderNodes(nodes) {
  const list = document.getElementById("nodes-list");
  list.innerHTML = "";

  for (const node of nodes) {
    const item = document.createElement("li");
    item.className = "node-row";

    const dot = document.createElement("span");
    dot.className = "node-dot";
    dot.style.color = node.accent_color;
    dot.style.background = node.accent_color;

    const copy = document.createElement("span");
    copy.className = "node-copy";

    const label = document.createElement("strong");
    label.textContent = node.label;
    const description = document.createElement("span");
    description.textContent = node.description;
    copy.append(label, description);

    const meta = document.createElement("span");
    meta.className = "node-meta";
    meta.textContent = node.slug;

    item.append(dot, copy, meta);
    list.appendChild(item);
  }
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

  setText("prefix-value", config.urlPrefix || "/");

  try {
    const payload = await fetchBootstrap(config.apiBase);
    renderNodes(payload.sampleNodes);
    renderer.setNodes(payload.sampleNodes);
    setText("mode-value", payload.app.mode);
    setText("api-value", "Online");
    setText("db-value", payload.health.database);
    updateHealthPill(payload.health.status === "ok");
  } catch (error) {
    console.error(error);
    setText("api-value", "Error");
    setText("db-value", "Unknown");
    updateHealthPill(false);
  }
}


bootstrap();
