# Movie App — AI Recommendations (Local TF-IDF)

## What this app does
- Browse a seeded catalog of **movies / series / anime**
- Save items to your **Library** (SQLite)
- Get **recommendations** generated locally using **TF‑IDF + cosine similarity** over each item’s text (kind/title/genres/keywords/synopsis)

## Stack
- Backend: **FastAPI** + **SQLite**
- Recommender: **local TF‑IDF** (no external AI calls)
- Frontend: **vanilla HTML/JS**

## Run
### Fast path
From the project root:

```bat
run_backend.bat
```

For Android/emulator or phone testing through ngrok:

```bat
start_app.bat ngrok
```

That starts/verifies the FastAPI backend, starts ngrok on port `8001`, writes the public HTTPS URL into `frontend\api-config.js`, and launches the Android app if an emulator/device is connected.

To go back to local backend fallback URLs:

```bat
start_app.bat
```

### 1) Backend (FastAPI)
From the project root: `c:/Users/Mae/Downloads/Movie App/`

```bat
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
backend\.venv\Scripts\python.exe -m backend.seed
backend\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

### Expand the movie database
The app includes a local starter catalog and can expand from TMDB online. Create a TMDB API key/token, then set one of these environment variables before starting the backend:

```bat
set TMDB_API_KEY=your_tmdb_api_key
```

or:

```bat
set TMDB_BEARER_TOKEN=your_tmdb_bearer_token
```

With the backend running, press **Online Import** in the app to import more movies into SQLite and refresh recommendations.

You can also import from the command line:

```bat
backend\.venv\Scripts\python.exe -m backend.import_tmdb --source discover --pages 25
```

Each TMDB page has up to 20 movies, so `--pages 25` imports up to about 500 movies. The importer skips duplicate titles. Add `--skip-poster-data` to store online poster URLs only instead of embedding poster images in SQLite.

### 2) Frontend
Open:
- `frontend/index.html`

If the browser blocks requests due to CORS, ensure the backend allows origins (it currently allows `*`).

### 2b) Admin app
The admin console is a React + Vite + Tailwind + shadcn/ui SPA, also installable as a PWA. With the backend running, open:

- `http://localhost:8001/admin/`

The default token is `admin`; override it by setting `MOVIETAYO_ADMIN_TOKEN` in your backend environment. To modify or extend the admin app, see `admin-app/README.md` — source lives in `admin-app/`, the production build is committed to `admin/` so the backend serves it out of the box.

The frontend reads `frontend\api-config.js` first. Leave it empty for local fallback URLs, or set it with:

```bat
set_api_url.bat https://your-ngrok-url.ngrok-free.app
```

### 3) Android
The Android app is a native WebView wrapper around `frontend/index.html`.

From the project root, keep the backend running, then build:

```bat
cd android
C:\Users\Mae\.gradle\wrapper\dists\gradle-8.14.3-all\10utluxaxniiv4wxiphsi49nj\gradle-8.14.3\bin\gradle.bat assembleDebug
```

Install on a connected emulator/device:

```bat
%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe install -r app\build\outputs\apk\debug\app-debug.apk
```

On the Android emulator, the app calls the backend through `http://10.0.2.2:8001`, which maps to your computer.

When using ngrok, rebuild/install the APK after `start_app.bat ngrok` so the bundled `api-config.js` contains the current ngrok URL.

## API
- `GET /health`
- `GET /api/catalog`
- `GET /api/catalog/stats`
- `GET /api/catalog/search?q=...`
- `POST /api/catalog/import/tmdb` (body: `{pages, source, sort_by, min_votes, store_poster_data}`)
- `POST /api/watchlist/save` (body: `{content_id, liked, reflection}`)
- `GET /api/watchlist?user_id=demo`
- `GET /api/recommendations?user_id=demo&limit=10`
