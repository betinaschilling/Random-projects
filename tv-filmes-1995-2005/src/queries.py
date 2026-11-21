"""Faixas de filmes e consultas usadas na busca."""

# Faixa -> emissora. Nomes conforme a Wikipédia e a imprensa da época.
FAIXAS = {
    "Sessão da Tarde": "Globo",
    "Tela Quente": "Globo",
    "Supercine": "Globo",
    "Temperatura Máxima": "Globo",
    "Corujão": "Globo",
    "Domingo Maior": "Globo",
    "Cinema Especial": "Globo",
    "Sessão de Gala": "Globo",
    "Intercine": "Globo",
    "Campeões de Bilheteria": "Globo",
    "Sessão de Sábado": "Globo",
    "Cinema em Casa": "SBT",
    "Cine Espetacular": "SBT",
    "Tela de Sucessos": "SBT",
    "Sessão das Dez": "SBT",
    "Cine Belas Artes": "SBT",
    "Domingo no Cinema": "SBT",
    "Sessão Desenho": "SBT",
}

EMISSORAS = {
    "Globo": ["Rede Globo", "TV Globo"],
    "SBT": ["SBT", "Sistema Brasileiro de Televisão"],
}

# Faixas com nome ambíguo (clima, cinemas de rua) exigem emissora e "filme" na busca.
AMBIGUAS = {"Temperatura Máxima", "Corujão", "Sessão de Sábado", "Cine Belas Artes", "Cinema Especial", "Sessão de Gala"}

QUERIES = [f'"{f}" {FAIXAS[f]} filme' if f in AMBIGUAS else f'"{f}"' for f in FAIXAS] + [
    '"exibido pela Rede Globo" filme',
    '"exibido pelo SBT" filme',
    '"exibido na TV Globo" filme',
    '"estreou na TV aberta" filme',
    '"exibição na televisão" Globo filme',
    '"exibido pela primeira vez" Globo filme',
    '"exibido pela primeira vez" SBT filme',
]
