import argparse
import base64
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from sqlalchemy import inspect, text

from .db import SessionLocal, engine
from .models import ContentItem

TMDB_API_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


def ensure_column():
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns(ContentItem.__tablename__)}
    if "poster_data_url" in columns:
        return

    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE content_items ADD COLUMN poster_data_url TEXT"))


def tmdb_request(path: str, params: dict | None = None) -> dict:
    api_key = os.getenv("TMDB_API_KEY")
    bearer_token = os.getenv("TMDB_BEARER_TOKEN")
    if not api_key and not bearer_token:
        raise RuntimeError("Set TMDB_API_KEY or TMDB_BEARER_TOKEN before running this importer.")

    query = dict(params or {})
    if api_key:
        query["api_key"] = api_key

    url = f"{TMDB_API_BASE}{path}"
    if query:
        url = f"{url}?{urlencode(query)}"

    headers = {"Accept": "application/json", "User-Agent": "MovieAppImporter/1.0"}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    with urlopen(Request(url, headers=headers), timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_poster_data_url(poster_path: str | None, store_data_url: bool = True) -> tuple[str | None, str | None]:
    if not poster_path:
        return None, None

    image_url = f"{TMDB_IMAGE_BASE}{poster_path}"
    if not store_data_url:
        return image_url, None

    with urlopen(
        Request(image_url, headers={"User-Agent": "MovieAppImporter/1.0"}),
        timeout=30,
    ) as response:
        content_type = response.headers.get_content_type() or "image/jpeg"
        encoded = base64.b64encode(response.read()).decode("ascii")

    return image_url, f"data:{content_type};base64,{encoded}"


def genre_map() -> dict[int, str]:
    payload = tmdb_request("/genre/movie/list", {"language": "en-US"})
    return {item["id"]: item["name"] for item in payload.get("genres", [])}


def movie_keywords(movie_id: int) -> str:
    try:
        payload = tmdb_request(f"/movie/{movie_id}/keywords")
    except Exception:
        return ""

    words = [item.get("name", "") for item in payload.get("keywords", [])]
    return ", ".join([word for word in words if word][:8])


def import_movies(pages: int, source: str, sort_by: str, min_votes: int, store_posters: bool = True) -> dict:
    ensure_column()
    genres_by_id = genre_map()

    db = SessionLocal()
    try:
        existing_titles = {title for (title,) in db.query(ContentItem.title).all()}
        added = 0
        skipped = 0

        for page in range(1, pages + 1):
            if source == "popular":
                payload = tmdb_request("/movie/popular", {"language": "en-US", "page": page})
            else:
                payload = tmdb_request(
                    "/discover/movie",
                    {
                        "language": "en-US",
                        "include_adult": "false",
                        "include_video": "false",
                        "sort_by": sort_by,
                        "vote_count.gte": min_votes,
                        "page": page,
                    },
                )

            for movie in payload.get("results", []):
                title = (movie.get("title") or movie.get("original_title") or "").strip()
                if not title or title in existing_titles:
                    skipped += 1
                    continue

                genre_names = [genres_by_id.get(genre_id) for genre_id in movie.get("genre_ids", [])]
                genre_text = ", ".join([name for name in genre_names if name]) or "Movie"
                image_url, poster_data_url = fetch_poster_data_url(movie.get("poster_path"), store_data_url=store_posters)

                item = ContentItem(
                    kind="movie",
                    title=title,
                    genres=genre_text,
                    keywords=movie_keywords(movie["id"]),
                    synopsis=movie.get("overview") or "",
                    image_url=image_url,
                    poster_data_url=poster_data_url,
                )
                db.add(item)
                existing_titles.add(title)
                added += 1

            db.commit()
            print(f"Imported page {page}/{pages}; added={added}; skipped={skipped}")

        print(f"Done. Added {added} movies; skipped {skipped} duplicates or invalid rows.")
        return {"added": added, "skipped": skipped, "pages": pages}
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Bulk import movies from TMDB into SQLite.")
    parser.add_argument("--pages", type=int, default=5, help="Number of TMDB pages to import. Each page has up to 20 movies.")
    parser.add_argument("--source", choices=["popular", "discover"], default="discover")
    parser.add_argument("--sort-by", default="popularity.desc")
    parser.add_argument("--min-votes", type=int, default=250)
    parser.add_argument(
        "--skip-poster-data",
        action="store_true",
        help="Store online poster URLs only instead of embedding poster images in SQLite.",
    )
    args = parser.parse_args()

    if args.pages < 1:
        raise SystemExit("--pages must be at least 1")

    try:
        import_movies(
            pages=args.pages,
            source=args.source,
            sort_by=args.sort_by,
            min_votes=args.min_votes,
            store_posters=not args.skip_poster_data,
        )
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
