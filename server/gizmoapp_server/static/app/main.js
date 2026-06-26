import { SceneRenderer } from "./scene.js";


function readConfig() {
  const raw = document.getElementById("gizmoapp-config");
  return JSON.parse(raw.textContent);
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


function bootstrap() {
  const config = readConfig();
  const renderer = new SceneRenderer(document.getElementById("scene-canvas"));
  registerServiceWorker(config.serviceWorkerUrl);
  renderer.setNodes([]);
}


bootstrap();
