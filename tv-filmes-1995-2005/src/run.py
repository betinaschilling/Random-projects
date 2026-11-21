"""Pipeline: busca -> artigos -> menções -> CSV."""
from __future__ import annotations

import csv
import sys
from functools import lru_cache
from pathlib import Path

from bs4 import BeautifulSoup

from extract import como_dict, eh_filme, extrai
from queries import QUERIES
from wiki import article_url, fetch, search

OUT = Path(__file__).resolve().parents[1] / "data"


@lru_cache(maxsize=None)
def artigo_eh_filme(titulo: str) -> bool:
    html = fetch(article_url(titulo))
    return bool(html) and eh_filme(BeautifulSoup(html, "html.parser"))


def main() -> None:
    titulos: dict[str, str] = {}
    for q in QUERIES:
        for t in search(q):
            titulos.setdefault(t, q)
    print(f"{len(titulos)} artigos candidatos", file=sys.stderr, flush=True)
    linhas = []
    for i, (t, q) in enumerate(sorted(titulos.items()), 1):
        url = article_url(t)
        for d in como_dict(extrai(t, fetch(url), url, artigo_eh_filme)):
            d["consulta"] = q
            linhas.append(d)
        if i % 50 == 0:
            print(f"{i}/{len(titulos)} artigos, {len(linhas)} menções", file=sys.stderr, flush=True)
    OUT.mkdir(exist_ok=True)
    campos = ["titulo", "ano_lancamento", "emissora", "faixa", "ano_exibicao", "confianca", "origem", "trecho", "artigo", "url", "consulta"]
    linhas.sort(key=lambda d: (d["emissora"], d["ano_exibicao"], d["titulo"].lower()))
    with open(OUT / "mencoes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)
    print(f"{len(linhas)} menções -> {OUT / 'mencoes.csv'}", file=sys.stderr)


if __name__ == "__main__":
    main()
