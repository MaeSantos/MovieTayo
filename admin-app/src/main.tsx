import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "@/App";
import { AuthProvider } from "@/store/auth";
import { ThemeProvider } from "@/store/theme";
import "@/index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ThemeProvider>
      <AuthProvider>
        <App />
      </AuthProvider>
    </ThemeProvider>
  </React.StrictMode>
);

// Register the service worker for PWA install / offline shell support.
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => {
      // Service worker registration is best-effort; ignore errors.
    });
  });
}
