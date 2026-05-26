(function () {
  const catalog = Array.isArray(window.MOVIETAYO_LOCAL_CATALOG) ? window.MOVIETAYO_LOCAL_CATALOG : [];
  const savedKey = "movietayo.localBackend.saved";
  const behaviorKey = "movietayo.localBackend.behavior";

  function readJson(key, fallback) {
    try {
      return JSON.parse(localStorage.getItem(key) || "null") || fallback;
    } catch (_) {
      return fallback;
    }
  }

  function writeJson(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  function savedItems() {
    return readJson(savedKey, []);
  }

  function behaviorItems() {
    return readJson(behaviorKey, []);
  }

  function parsePath(path) {
    return new URL(path, "https://local.movietayo");
  }

  function itemText(item) {
    return [item.title, item.kind, item.genres, item.keywords, item.synopsis].join(" ").toLowerCase();
  }

  function popular(limit) {
    const preferred = [
      "Blade Runner 2049",
      "The Matrix",
      "The Dark Knight",
      "Avengers: Endgame",
      "Interstellar",
      "Inception",
      "Fight Club",
      "The Godfather",
      "The Shawshank Redemption",
      "Stranger Things",
    ];
    const byTitle = new Map(catalog.map((item) => [item.title, item]));
    const ranked = preferred.map((title) => byTitle.get(title)).filter(Boolean);
    const used = new Set(ranked.map((item) => item.id));
    return ranked.concat(catalog.filter((item) => !used.has(item.id))).slice(0, limit);
  }

  function recommendations(limit, refresh = 0) {
    const saved = savedItems().filter((item) => item.liked !== false);
    const savedIds = new Set(saved.map((item) => item.content_id));
    const savedCatalog = catalog.filter((item) => savedIds.has(item.id));
    const genreScores = new Map();

    savedCatalog.forEach((item) => {
      String(item.genres || "").split(",").map((genre) => genre.trim().toLowerCase()).filter(Boolean).forEach((genre) => {
        genreScores.set(genre, (genreScores.get(genre) || 0) + 1);
      });
    });

    const scored = catalog
      .filter((item) => !savedIds.has(item.id))
      .map((item) => {
        const genres = String(item.genres || "").split(",").map((genre) => genre.trim().toLowerCase()).filter(Boolean);
        const matches = genres.reduce((sum, genre) => sum + (genreScores.get(genre) || 0), 0);
        const score = savedCatalog.length ? Math.min(0.98, 0.55 + matches * 0.12) : 0.6;
        return { ...item, score };
      })
      .sort((a, b) => b.score - a.score || a.title.localeCompare(b.title));

    if (!scored.length) return [];

    const pageCount = Math.max(1, Math.ceil(scored.length / limit));
    const page = Math.abs(Number(refresh) || 0) % pageCount;
    const start = page * limit;
    const rotated = scored.slice(start).concat(scored.slice(0, start));
    return rotated.slice(0, limit);
  }

  async function saveWatchlist(body) {
    const contentId = Number(body.content_id);
    if (!catalog.some((item) => item.id === contentId)) {
      throw new Error("Invalid content_id");
    }

    const saved = savedItems();
    const existing = saved.find((item) => item.content_id === contentId);
    if (existing) {
      existing.liked = body.liked !== false;
      existing.reflection = body.reflection || "";
      writeJson(savedKey, saved);
      return existing;
    }

    const next = {
      id: Date.now(),
      content_id: contentId,
      liked: body.liked !== false,
      reflection: body.reflection || "",
    };
    saved.unshift(next);
    writeJson(savedKey, saved);
    return next;
  }

  window.MOVIETAYO_LOCAL_BACKEND = {
    enabled: /Android/i.test(navigator.userAgent),
    async request(path, opts = {}) {
      const url = parsePath(path);
      const method = String(opts.method || "GET").toUpperCase();
      const body = opts.body ? JSON.parse(opts.body) : {};

      if (url.pathname === "/health") return { ok: true, local: true };
      if (url.pathname === "/api/catalog/stats") return { total: catalog.length, online_import_ready: false, local: true };
      if (url.pathname === "/api/catalog" && method === "GET") return catalog;
      if (url.pathname === "/api/catalog/search" && method === "GET") {
        const query = (url.searchParams.get("q") || "").trim().toLowerCase();
        return query ? catalog.filter((item) => itemText(item).includes(query)).slice(0, 30) : catalog.slice(0, 30);
      }
      if (url.pathname === "/api/catalog/popular" && method === "GET") {
        return popular(Number(url.searchParams.get("limit") || 10));
      }
      if (url.pathname === "/api/watchlist" && method === "GET") return savedItems();
      if (url.pathname === "/api/watchlist/save" && method === "POST") return saveWatchlist(body);
      if (url.pathname === "/api/recommendations" && method === "GET") {
        return {
          user_id: url.searchParams.get("user_id") || "demo",
          recommendations: recommendations(
            Number(url.searchParams.get("limit") || 10),
            Number(url.searchParams.get("refresh") || 0)
          ),
        };
      }
      if (url.pathname === "/api/behavior/track" && method === "POST") {
        const behavior = behaviorItems();
        behavior.push({ ...body, id: Date.now(), created_at: new Date().toISOString() });
        writeJson(behaviorKey, behavior.slice(-250));
        return { status: "tracked", id: behavior[behavior.length - 1].id, local: true };
      }

      throw new Error(`Local backend route not found: ${method} ${url.pathname}`);
    },
  };
})();
