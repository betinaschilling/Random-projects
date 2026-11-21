from extract import RE_GLOBO, extrai

def pagina(corpo: str, categorias=()) -> str:
    cats = "".join(f'<li><a>{c}</a></li>' for c in categorias)
    return f'<div id="mw-content-text"><div class="mw-parser-output">{corpo}</div></div><div id="mw-normal-catlinks"><ul>{cats}</ul></div>'


def test_artigo_de_filme_com_faixa_e_ano():
    html = pagina("<p>O filme foi exibido pela primeira vez na Tela Quente em 1998.</p>", ["Filmes dos Estados Unidos de 1995"])
    [m] = extrai("Jumanji (filme)", html, "u")
    assert (m.titulo, m.emissora, m.faixa, m.ano_exibicao, m.confianca) == ("Jumanji", "Globo", "Tela Quente", 1998, "alta")
    assert m.ano_lancamento == 1995


def test_ano_fora_do_periodo_e_ignorado():
    html = pagina("<p>Foi exibido pelo SBT em 2010.</p>", ["Filmes de 1990"])
    assert extrai("X (filme)", html, "u") == []


def test_exige_verbo_de_exibicao():
    html = pagina("<p>Em 1997 a Globo comprou os direitos.</p>", ["Filmes de 1990"])
    assert extrai("X (filme)", html, "u") == []


def test_globo_filmes_e_globo_de_ouro_nao_contam():
    assert not RE_GLOBO.search("produzido pela Globo Filmes")
    assert not RE_GLOBO.search("indicado ao Globo de Ouro")
    assert RE_GLOBO.search("exibido pela Rede Globo")


def test_artigo_que_nao_e_filme_so_aceita_links_de_filme():
    corpo = ('<p>Em 2000, o Cinema Especial exibiu o filme <i><a title="Titanic (filme de 1997)">Titanic</a></i> '
             'logo após <i><a title="Zorra Total">Zorra Total</a></i>.</p>')
    ms = extrai("Cinema Especial", pagina(corpo), "u")
    assert [m.titulo for m in ms] == ["Titanic"]
    assert ms[0].faixa == "Cinema Especial" and ms[0].ano_exibicao == 2000


def test_exibicao_antes_do_lancamento_e_descartada():
    html = pagina("<p>Exibido pela Rede Globo em 1996.</p>", ["Filmes de 2001"])
    assert extrai("Y (filme)", html, "u") == []


def test_ano_entre_parenteses_e_lancamento():
    corpo = '<p>Entre os filmes estão <i><a title="Guerra de Canudos (filme)">Guerra de Canudos</a></i> (1997), também exibido pela Rede Globo como minissérie.</p>'
    assert extrai("Sérgio Rezende", pagina(corpo), "u", lambda t: True) == []


def test_serie_de_tv_nao_e_filme():
    html = pagina("<p>Foi reprisado pela Rede Globo em 2003.</p>", ["Filmes de anime", "Séries de televisão de anime de 2001"])
    assert extrai("Digimon Tamers", html, "u") == []
