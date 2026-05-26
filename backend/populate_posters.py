import base64
import json
import mimetypes
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from sqlalchemy import inspect, text

from .db import SessionLocal, engine
from .models import ContentItem

PAGE_TITLES = {
    "Inception": "Inception",
    "Interstellar": "Interstellar (film)",
    "Stranger Things": "Stranger Things",
    "Fullmetal Alchemist: Brotherhood": "Fullmetal Alchemist: Brotherhood",
    "Attack on Titan": "Attack on Titan",
    "The Matrix": "The Matrix",
    "Breaking Bad": "Breaking Bad",
    "Demon Slayer: Kimetsu no Yaiba": "Demon Slayer: Kimetsu no Yaiba",
    "The Dark Knight": "The Dark Knight",
    "Pulp Fiction": "Pulp Fiction",
}

TMDB_PAGES = {
    "Inception": ("movie", 27205),
    "Interstellar": ("movie", 157336),
    "Stranger Things": ("tv", 66732),
    "Fullmetal Alchemist: Brotherhood": ("tv", 31911),
    "Attack on Titan": ("tv", 1429),
    "The Matrix": ("movie", 603),
    "Breaking Bad": ("tv", 1396),
    "Demon Slayer: Kimetsu no Yaiba": ("tv", 85937),
    "The Dark Knight": ("movie", 155),
    "Pulp Fiction": ("movie", 680),
    "Avatar": ("movie", 19995),
    "Avengers: Endgame": ("movie", 299534),
    "Titanic": ("movie", 597),
    "Joker": ("movie", 475557),
    "Parasite": ("movie", 496243),
    "Spirited Away": ("movie", 129),
    "Your Name.": ("movie", 372058),
    "Toy Story": ("movie", 862),
    "Finding Nemo": ("movie", 12),
    "The Lion King": ("movie", 8587),
    "Gladiator": ("movie", 98),
    "Fight Club": ("movie", 550),
    "Forrest Gump": ("movie", 13),
    "The Shawshank Redemption": ("movie", 278),
    "The Godfather": ("movie", 238),
    "Goodfellas": ("movie", 769),
    "Dune: Part Two": ("movie", 693134),
    "Oppenheimer": ("movie", 872585),
    "Barbie": ("movie", 346698),
    "Spider-Man: Into the Spider-Verse": ("movie", 324857),
    "Black Panther": ("movie", 284054),
    "Mad Max: Fury Road": ("movie", 76341),
    "La La Land": ("movie", 313369),
    "Whiplash": ("movie", 244786),
    "Coco": ("movie", 354912),
    "Inside Out": ("movie", 150540),
    "The Social Network": ("movie", 37799),
    "Everything Everywhere All at Once": ("movie", 545611),
    "John Wick": ("movie", 245891),
    "Knives Out": ("movie", 546554),
}


def ensure_column():
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns(ContentItem.__tablename__)}
    if "poster_data_url" in columns:
        return

    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE content_items ADD COLUMN poster_data_url TEXT"))


def fetch_data_url(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 MovieAppPosterLoader/1.0",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=30) as response:
        data = response.read()
        content_type = response.headers.get_content_type()

    if not content_type or content_type == "application/octet-stream":
        content_type = mimetypes.guess_type(url)[0] or "image/jpeg"

    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{content_type};base64,{encoded}"


def wikipedia_image_url(title: str) -> str | None:
    page_title = PAGE_TITLES.get(title, title)
    params = urlencode(
        {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "piprop": "thumbnail|original",
            "pithumbsize": "700",
            "titles": page_title,
            "redirects": "1",
        }
    )
    url = f"https://en.wikipedia.org/w/api.php?{params}"
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 MovieAppPosterLoader/1.0"})

    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    pages = payload.get("query", {}).get("pages", {})
    for page in pages.values():
        thumbnail = page.get("thumbnail", {})
        original = page.get("original", {})
        return thumbnail.get("source") or original.get("source")

    return None


def tmdb_poster_url(title: str) -> str | None:
    page = TMDB_PAGES.get(title)
    if not page:
        return None

    kind, tmdb_id = page
    url = f"https://www.themoviedb.org/{kind}/{tmdb_id}/images/posters?language=en-US"
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 MovieAppPosterLoader/1.0"})

    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="ignore")

    match = re.search(r"https://image\.tmdb\.org/t/p/original/[A-Za-z0-9]+\.jpg", html)
    return match.group(0) if match else None


def candidate_urls(item: ContentItem) -> list[str]:
    urls = []
    try:
        tmdb_url = tmdb_poster_url(item.title)
        if tmdb_url:
            urls.append(tmdb_url)
    except Exception as exc:
        print(f"TMDB lookup failed: {item.title} ({exc})")

    if item.image_url:
        urls.append(item.image_url)

    try:
        wiki_url = wikipedia_image_url(item.title)
        if wiki_url:
            urls.append(wiki_url)
    except Exception as exc:
        print(f"Wikipedia lookup failed: {item.title} ({exc})")

    return urls


def main():
    ensure_column()

    db = SessionLocal()
    try:
        items = db.query(ContentItem).order_by(ContentItem.id.asc()).all()
        for item in items:
            urls = candidate_urls(item)
            if not urls:
                print(f"Missing image URL: {item.title}")
                continue

            for url in urls:
                try:
                    print(f"Downloading poster: {item.title} <- {url}")
                    item.poster_data_url = fetch_data_url(url)
                    item.image_url = url
                    break
                except Exception as exc:
                    print(f"Failed: {item.title} <- {url} ({exc})")

            if not item.poster_data_url:
                print(f"Could not store poster: {item.title}")

        db.commit()
        print("Stored poster images in the database.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
