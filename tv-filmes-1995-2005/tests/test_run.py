from run import consolida


def linha(titulo, conf, ano=2000, emissora="Globo"):
    return {"titulo": titulo, "confianca": conf, "ano_exibicao": ano, "emissora": emissora}


def test_consolida_remove_baixa_e_duplicatas():
    out = consolida([linha("Napoleon (1995)", "alta"), linha("Napoleon", "media"), linha("Jubiabá", "baixa"), linha("Titanic", "media"), linha("Titanic", "alta")])
    assert sorted((d["titulo"], d["confianca"]) for d in out) == [("Napoleon", "alta"), ("Titanic", "alta")]
