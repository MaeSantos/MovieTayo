# MovieTayo Admin — Installable App

A modern admin console built with **React + Vite + TypeScript + Tailwind CSS + shadcn/ui**, served by the existing FastAPI backend at `/admin`. It's also a **PWA** — install it from your browser's address bar to launch it as a standalone window on desktop or as a home-screen app on mobile.

## What it manages
- **Dashboard** — catalog/user/save/event counts, top genres bar chart, top saved movies.
- **Reports** — filter by status, inline status update with toast feedback.
- **Users** — saved/event/report counts plus top genres and recent searches.
- **Catalog** — debounced search, sortable columns, image/poster-data status.
- **Behavior** — interaction events with time-ago and context viewer.

All data is fetched from the existing `/api/admin/*` endpoints using the `X-Admin-Token` header (default token: `admin`; override with the `MOVIETAYO_ADMIN_TOKEN` env var on the backend).

## Run the built app

The build output is committed to `../admin/`, so once you start the FastAPI backend on port `8001` you can open:

```
http://localhost:8001/admin/
```

No additional steps required.

## Develop locally

From this directory:

```bash
npm install
npm run dev
```

Vite serves the app on `http://localhost:5173` and proxies `/api/*` and `/health` to the FastAPI backend on `http://localhost:8001` — so just keep the backend running in another terminal.

## Build

```bash
npm run build
```

This compiles TypeScript and emits the production bundle into `../admin/` (overwriting the previous build). Commit the changes if you want the new build to be served by the backend.

## Lint / Typecheck

```bash
npm run typecheck
npm run lint     # ESLint is configured but optional
```

## PWA

- `public/manifest.webmanifest` — app metadata.
- `public/sw.js` — minimal service worker caching the app shell (API calls always go to the network).
- Icons are generated from the repo's `Logo.png` and live under `public/icons/`.

When you visit `/admin/` on Chrome/Edge, an install prompt appears in the address bar. On iOS Safari, use "Add to Home Screen".

## Project layout

```
admin-app/
├─ public/
│  ├─ icons/                 192/512/maskable PNG icons (from Logo.png)
│  ├─ manifest.webmanifest
│  └─ sw.js
├─ src/
│  ├─ App.tsx                Auth gate + app shell wiring
│  ├─ main.tsx               Entry point (+ service-worker registration)
│  ├─ index.css              Tailwind layers + design tokens
│  ├─ components/
│  │  ├─ ui/                 shadcn/ui-style primitives
│  │  ├─ layout/             Sidebar, Topbar, nav config
│  │  └─ dashboard/          StatCard
│  ├─ pages/                 Login, Dashboard, Reports, Users, Catalog, Behavior
│  ├─ store/                 Auth + theme React contexts
│  ├─ hooks/                 useDebounce
│  └─ lib/                   API client + utilities
├─ index.html
├─ vite.config.ts            outDir = ../admin, dev proxy to :8001
├─ tailwind.config.js
├─ postcss.config.js
├─ tsconfig*.json
└─ package.json
```
