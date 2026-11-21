"""Acesso educado à Wikipédia em português (HTML), com cache em disco."""
from __future__ import annotations

import hashlib
import os
import time
import urllib.parse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://pt.wikipedia.org"
UA = "tv-film-list-research/0.1 (generic research client)"
CACHE = Path(os.getenv("WIKI_CACHE", Path(__file__).resolve().parents[1] / ".cache"))
DELAY = float(os.getenv("WIKI_DELAY", "2"))

_session = requests.Session()
_session.headers["User-Agent"] = UA


def fetch(url: str) -> str:
    """Baixa uma URL com cache e pausa entre requisições; tenta de novo em 429/5xx."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (hashlib.sha1(url.encode()).hexdigest() + ".html")
    if path.exists():
        return path.read_text(encoding="utf-8")
    for attempt in range(5):
        r = _session.get(url, timeout=40)
        time.sleep(DELAY)
        if r.status_code == 200:
            path.write_text(r.text, encoding="utf-8")
            return r.text
        if r.status_code == 404:
            return ""
        time.sleep(15 * (attempt + 1))
    r.raise_for_status()
    return ""


def search(query: str, limit: int = 500) -> list[str]:
    """Títulos de artigos (espaço principal) que contêm a consulta em texto completo."""
    titles: list[str] = []
    offset = 0
    while True:
        q = urllib.parse.urlencode({"search": query, "fulltext": 1, "ns0": 1, "limit": limit, "offset": offset})
        soup = BeautifulSoup(fetch(f"{BASE}/w/index.php?{q}"), "html.parser")
        page = [a.get_text() for a in soup.select(".mw-search-result-heading a")]
        titles += page
        if len(page) < limit or offset >= 1000:
            return titles
        offset += limit


def article_url(title: str) -> str:
    return f"{BASE}/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
