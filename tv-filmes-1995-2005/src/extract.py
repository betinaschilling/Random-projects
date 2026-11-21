"""Extrai menções de exibição de filmes na Globo e no SBT (1995-2005) de artigos da Wikipédia."""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict

from typing import Callable

from bs4 import BeautifulSoup

from queries import FAIXAS

ANO_MIN, ANO_MAX = 1995, 2005

# "Globo" sozinho é ambíguo: exclui Globo Filmes, Globo de Ouro, GloboNews etc.
RE_GLOBO = re.compile(
    r"\b(?:Rede Globo|TV Globo|Globo)(?!\s*(?:Filmes|de Ouro|News|Repórter|Rural|Esporte|Comunicação|Marcas|sat|play|Play|\.com))\b"
)
RE_SBT = re.compile(r"\bSBT\b|Sistema Brasileiro de Televisão")
RE_EXIB = re.compile(
    r"exibi|exibid|transmiti|transmitid|reprisad|reprise|foi ao ar|levad[oa] ao ar|estre(?:ou|ia) na (?:TV|televisão)"
    r"|televisão aberta|TV aberta|passou na|passado na|apresentad[oa] (?:na|pela|pelo)",
    re.I,
)
RE_ANO = re.compile(r"(?<!\d)(19\d\d|20\d\d)(?!\d)")
RE_FRASE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý\"“(])")
RE_PAREN = re.compile(r"\s*\((?:filme|telefilme|curta-metragem)[^)]*\)$", re.I)
JANELA = 120  # caracteres após a menção à emissora/faixa em que o ano deve aparecer


@dataclass
class Mencao:
    titulo: str
    ano_lancamento: int | None
    emissora: str
    faixa: str
    ano_exibicao: int
    confianca: str
    origem: str
    trecho: str
    artigo: str
    url: str


def _limpa(soup: BeautifulSoup) -> BeautifulSoup:
    body = soup.select_one("#mw-content-text .mw-parser-output") or soup
    for sel in ("sup.reference", "table.navbox", "div.navbox", ".mw-editsection", "style", "table.ambox", "div.reflist", "ol.references"):
        for el in body.select(sel):
            el.decompose()
    return body


def eh_filme(soup: BeautifulSoup) -> bool:
    cats = [a.get_text() for a in soup.select("#mw-normal-catlinks li a")]
    if any(c.startswith(("Séries de televisão", "Programas de televisão", "Programas da", "Programas do", "Telenovelas", "Minisséries", "Animes", "Séries de animação", "Desenhos animados")) for c in cats):
        return False
    return any(c.startswith(("Filmes", "Telefilmes")) for c in cats)


def ano_lancamento(titulo: str, soup: BeautifulSoup) -> int | None:
    m = re.search(r"\((?:filme|telefilme)[^)]*?(\d{4})\)", titulo)
    if m:
        return int(m.group(1))
    for cat in soup.select("#mw-normal-catlinks li a"):
        m = re.fullmatch(r"Filmes (?:do|da|de|dos|das)? ?.*?(?:de )?(\d{4})", cat.get_text())
        if m and cat.get_text().startswith("Filmes") and re.search(r"de \d{4}$", cat.get_text()):
            return int(m.group(1))
    return None


def _menciona(frase: str) -> list[tuple[str, str, int]]:
    """Lista (emissora, faixa, posição) mencionadas na frase."""
    achados: list[tuple[str, str, int]] = []
    for faixa, emissora in FAIXAS.items():
        for m in re.finditer(re.escape(faixa), frase):
            achados.append((emissora, faixa, m.end()))
    for m in RE_GLOBO.finditer(frase):
        achados.append(("Globo", "", m.end()))
    for m in RE_SBT.finditer(frase):
        achados.append(("SBT", "", m.end()))
    return achados


def _anos_proximos(frase: str, pos: int) -> list[int]:
    anos = []
    for m in RE_ANO.finditer(frase):
        # aceita o ano até JANELA caracteres depois da menção, ou até 60 antes ("Em 1998, a Globo exibiu")
        if frase[max(0, m.start() - 1):m.start()] == "(" and frase[m.end():m.end() + 1] == ")":
            continue  # "Título (1997)": ano de lançamento
        if pos - 60 - len("Globo") <= m.start() <= pos + JANELA:
            a = int(m.group(1))
            if ANO_MIN <= a <= ANO_MAX:
                anos.append(a)
    return anos


def _frases(body: BeautifulSoup):
    """Gera (frase, {texto do título: artigo linkado ou None}) para títulos em itálico/links."""
    for el in body.find_all(["p", "li", "dd"]):
        if el.find_parent(["table"]):
            continue
        texto = re.sub(r"\s+", " ", el.get_text(" ", strip=True)).replace(" ,", ",").replace(" .", ".")
        if not texto:
            continue
        candidatos: dict[str, str | None] = {}
        for i in el.find_all("i"):
            t = i.get_text(" ", strip=True)
            a = i.find("a", title=True) or i.find_parent("a", title=True)
            if 2 <= len(t) <= 80:
                candidatos[t] = a["title"] if a else None
        for a in el.find_all("a", title=True):
            if re.search(r"\((?:filme|telefilme)", a["title"]):
                candidatos[a.get_text(" ", strip=True)] = a["title"]
        for frase in RE_FRASE.split(texto):
            yield frase, {t: l for t, l in candidatos.items() if t and t in frase}


def extrai(titulo: str, html: str, url: str, artigo_eh_filme: Callable[[str], bool] = lambda t: False) -> list[Mencao]:
    """`artigo_eh_filme(titulo)` confirma se um artigo linkado é de filme (pode buscar na rede)."""
    soup = BeautifulSoup(html, "html.parser")
    filme = eh_filme(soup)
    lanc = ano_lancamento(titulo, soup) if filme else None
    body = _limpa(soup)
    out: list[Mencao] = []
    for frase, italicos in _frases(body):
        if not RE_EXIB.search(frase):
            continue
        for emissora, faixa, pos in _menciona(frase):
            for ano in _anos_proximos(frase, pos):
                confianca = "alta" if faixa else "media"
                if filme:
                    alvos = [(RE_PAREN.sub("", titulo), lanc, "artigo do filme")]
                else:
                    # em artigos que não são de filme, só aceita títulos em itálico/links de filme na frase
                    alvos = []
                    for t, link in italicos.items():
                        if t in FAIXAS:
                            continue
                        if link and (re.search(r"\((?:filme|telefilme)", link) or artigo_eh_filme(link)):
                            alvos.append((RE_PAREN.sub("", link) if link.lower().startswith(t.lower()[:4]) else t, None, f"citado em '{titulo}'"))
                    confianca = "media" if faixa else "baixa"
                for t, al, origem in alvos:
                    if lanc and ano < lanc:
                        continue
                    out.append(Mencao(t, al, emissora, faixa, ano, confianca, origem, frase[:400], titulo, url))
    # deduplica por (titulo, emissora, faixa, ano)
    vistos, unicos = set(), []
    for m in sorted(out, key=lambda m: (m.faixa == "",)):
        k = (m.titulo.lower(), m.emissora, m.ano_exibicao)
        if k in vistos:
            continue
        vistos.add(k)
        unicos.append(m)
    return unicos


def como_dict(ms: list[Mencao]) -> list[dict]:
    return [asdict(m) for m in ms]
