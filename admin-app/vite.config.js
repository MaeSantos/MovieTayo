import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
// Build into the repo's existing /admin folder so FastAPI's StaticFiles
// mount at /admin keeps serving the SPA with zero backend changes.
export default defineConfig({
    base: "./",
    plugins: [react()],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
    build: {
        outDir: path.resolve(__dirname, "../admin"),
        emptyOutDir: true,
        sourcemap: false,
        assetsDir: "assets",
    },
    server: {
        port: 5173,
        proxy: {
            "/api": {
                target: "http://localhost:8001",
                changeOrigin: true,
            },
            "/health": {
                target: "http://localhost:8001",
                changeOrigin: true,
            },
        },
    },
});
