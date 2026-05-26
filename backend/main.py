from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

from .db import engine
from .models import Base
from .routes import admin, behavior, catalog, recommendations, watchlist

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MovieTayo - AI Recommendations")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalog.router, prefix="/api")
app.include_router(watchlist.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(behavior.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

@app.get("/health")
def health():
    return {"ok": True}

# Serve admin SPA and static files.
admin_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "admin")
if os.path.exists(admin_path):
    @app.get("/admin")
    @app.get("/admin/")
    def admin_index():
        return FileResponse(os.path.join(admin_path, "index.html"))

    @app.get("/admin/{path:path}")
    def admin_file_or_spa(path: str):
        requested = os.path.abspath(os.path.join(admin_path, path))
        admin_root = os.path.abspath(admin_path)
        if requested.startswith(admin_root) and os.path.isfile(requested):
            return FileResponse(requested)
        return FileResponse(os.path.join(admin_path, "index.html"))

# Serve Frontend static files from the root /
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
