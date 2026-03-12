import { fetchBootstrap } from "../api.js";
import { setupInstallControls } from "../install.js";


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
  const pill = document.getElementById("text-health-pill");
  pill.dataset.state = healthy ? "healthy" : "degraded";
  pill.textContent = healthy ? "Healthy" : "Degraded";
}


function renderRows(nodes) {
  const rows = document.getElementById("nodes-list");
  rows.innerHTML = "";

  for (const node of nodes) {
    const row = document.createElement("div");
    row.className = "table-row";

    const label = document.createElement("span");
    label.textContent = node.label;

    const slug = document.createElement("span");
    slug.textContent = node.slug;

    const position = document.createElement("span");
    position.textContent = `${node.x.toFixed(2)}, ${node.y.toFixed(2)}`;

    row.append(label, slug, position);
    rows.appendChild(row);
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
  setupInstallControls({
    button: document.getElementById("install-button"),
    hint: document.getElementById("install-hint"),
    appName: config.appName,
  });
  registerServiceWorker(config.serviceWorkerUrl);

  setText("prefix-value", config.urlPrefix || "/");

  try {
    const payload = await fetchBootstrap(config.apiBase);
    renderRows(payload.sampleNodes);
    setText("mode-value", payload.app.mode);
    setText("shell-value", payload.app.shellLabel);
    setText("db-value", payload.health.database);
    updateHealthPill(payload.health.status === "ok");
  } catch (error) {
    console.error(error);
    setText("db-value", "Error");
    updateHealthPill(false);
  }
}


bootstrap();
