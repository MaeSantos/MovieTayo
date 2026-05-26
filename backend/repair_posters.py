import argparse
import re
import time
from urllib.parse import quote
from urllib.request import Request, urlopen

from .db import SessionLocal
from .models import ContentItem

USER_AGENT = "Mozilla/5.0 MovieAppPosterRepair/1.0"


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    with urlopen(request, timeout=12) as response:
        return response.read().decode("utf-8", errors="ignore")


def is_live_image(url: str | None) -> bool:
    if not url:
        return False

    try:
        request = Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=4) as response:
            return response.status < 400
    except Exception:
        return False


def tmdb_kind(kind: str) -> str:
    return "tv" if kind in {"series", "anime"} else "movie"


def find_tmdb_path(title: str, kind: str) -> str | None:
    wanted_kind = tmdb_kind(kind)
    html = fetch_text(f"https://www.themoviedb.org/search?query={quote(title)}")
    paths = re.findall(rf"/{wanted_kind}/[0-9]+[-a-z0-9]*", html, flags=re.IGNORECASE)
    if paths:
        return paths[0]

    fallback_paths = re.findall(r"/(?:movie|tv)/[0-9]+[-a-z0-9]*", html, flags=re.IGNORECASE)
    return fallback_paths[0] if fallback_paths else None


def find_poster_url(title: str, kind: str) -> str | None:
    path = find_tmdb_path(title, kind)
    if not path:
        return None

    html = fetch_text(f"https://www.themoviedb.org{path}/images/posters?language=en-US")
    matches = re.findall(r"https://image\.tmdb\.org/t/p/original/[A-Za-z0-9._-]+\.jpg", html)
    return matches[0] if matches else None


def repair(limit: int | None = None, force: bool = False, delay: float = 0.35):
    db = SessionLocal()
    try:
        items = db.query(ContentItem).order_by(ContentItem.id.asc()).all()
        if limit:
            items = items[:limit]

        checked = 0
        repaired = 0
        failed = 0

        for item in items:
            checked += 1
            if not force and is_live_image(item.image_url):
                print(f"OK: {item.title}", flush=True)
                continue

            try:
                poster_url = find_poster_url(item.title, item.kind)
                if poster_url and is_live_image(poster_url):
                    item.image_url = poster_url
                    item.poster_data_url = None
                    db.add(item)
                    db.commit()
                    repaired += 1
                    print(f"FIXED: {item.title} -> {poster_url}", flush=True)
                else:
                    failed += 1
                    print(f"FAILED: {item.title}", flush=True)
            except Exception as exc:
                failed += 1
                print(f"FAILED: {item.title} ({exc})", flush=True)

            time.sleep(delay)

        print(f"Poster repair done. checked={checked} repaired={repaired} failed={failed}", flush=True)
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Repair broken movie poster URLs using TMDB public pages.")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--force", action="store_true", help="Refresh every poster URL, even if it currently loads.")
    parser.add_argument("--delay", type=float, default=0.35)
    args = parser.parse_args()
    repair(limit=args.limit, force=args.force, delay=args.delay)


if __name__ == "__main__":
    main()
