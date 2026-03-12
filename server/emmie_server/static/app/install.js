function isIos() {
  return /iphone|ipad|ipod/i.test(window.navigator.userAgent);
}


function isStandalone() {
  return window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
}


export function setupInstallControls({ button, hint, appName }) {
  let deferredPrompt = null;

  if (isStandalone()) {
    hint.textContent = `${appName} is already running in standalone mode.`;
    return;
  }

  if (!window.isSecureContext) {
    hint.textContent = "Install mode requires HTTPS on iPhone and Chromium-based browsers.";
    return;
  }

  if (isIos()) {
    hint.textContent = "On iPhone or iPad, use Share > Add to Home Screen to install this app.";
  }

  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    deferredPrompt = event;
    button.hidden = false;
    hint.textContent = "Install is available on this browser.";
  });

  button.addEventListener("click", async () => {
    if (!deferredPrompt) {
      return;
    }

    deferredPrompt.prompt();
    await deferredPrompt.userChoice;
    deferredPrompt = null;
    button.hidden = true;
    hint.textContent = `${appName} can now run in its standalone shell.`;
  });
}

