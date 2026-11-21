# Filmes exibidos na Globo e no SBT (1995–2005), a partir de fontes abertas

Lista **parcial** de filmes que a TV Globo e o SBT exibiram entre 1995 e 2005, extraída de artigos da Wikipédia em português. Cada linha traz o trecho que comprova a exibição e o link do artigo.

> **Não é uma lista completa.** A Wikipédia só registra exibições na TV quando um editor achou relevante, como estreias na TV aberta, recordes de audiência ou exibições especiais. Para chegar a uma lista completa seria preciso usar o roteiro de TV diário dos jornais da época. O do *Jornal do Brasil* está na Hemeroteca Digital da Biblioteca Nacional, mas a coleta automática exigiria contornar o captcha do leitor, e o material tem aviso de direito autoral. Por isso essa fonte ficou de fora (ver "Fontes descartadas").

## Como funciona

1. **Busca** (`src/queries.py`): busca no texto completo da Wikipédia pelo nome de cada faixa de filmes (Sessão da Tarde, Tela Quente, Supercine, Cinema em Casa, Cine Espetacular…) e por expressões como "exibido pela Rede Globo".
2. **Leitura** (`src/wiki.py`): baixa o HTML de cada artigo, com 2 s entre requisições e cache local em `.cache/`. A API `api.php` não é usada, porque estava limitando o IP de saída deste ambiente.
3. **Extração** (`src/extract.py`): guarda frases que contêm ao mesmo tempo:
   - a emissora (Globo/SBT) ou o nome de uma faixa;
   - um verbo de exibição (exibido, transmitido, reprisado, foi ao ar…);
   - um ano entre 1995 e 2005, próximo da menção à emissora.

   "Globo Filmes", "Globo de Ouro", "GloboNews" e similares não contam como a emissora.
4. **Título do filme**:
   - se o artigo é de um filme (categoria "Filmes…"), o título é o próprio artigo;
   - se não é (por exemplo, o artigo da faixa *Cinema Especial*), só valem títulos em itálico que linkam para um artigo de filme ou que aparecem sem link numa frase com a palavra "filme".

## Saída: `data/mencoes.csv`

| coluna | significado |
|---|---|
| `titulo` | título do filme como aparece na Wikipédia (pt) |
| `ano_lancamento` | ano de lançamento, quando dá para deduzir do título ou das categorias |
| `emissora` | `Globo` ou `SBT` |
| `faixa` | faixa citada no trecho (vazio se o trecho só cita a emissora) |
| `ano_exibicao` | ano entre 1995 e 2005 citado junto da exibição |
| `confianca` | `alta`: artigo do filme e faixa citada; `media`: só a emissora, ou citação em outro artigo com faixa; `baixa`: citação em outro artigo sem faixa |
| `origem` | `artigo do filme` ou `citado em '<artigo>'` |
| `trecho` | frase de onde a menção foi extraída (até 400 caracteres) |
| `artigo`, `url` | artigo da Wikipédia de onde saiu o trecho |
| `consulta` | busca que levou ao artigo |

### Resultado da coleta (novembro de 2026)

Foram lidos 1.407 artigos candidatos. Sobraram **16 menções, de 15 filmes distintos**: 10 na Globo e 6 no SBT. As linhas de confiança `baixa` foram descartadas porque todas eram falsos positivos. Problemas conhecidos nas linhas que ficaram:

- *Sexta-Feira 13*: o trecho fala da exibição na **Band** com a dublagem da Globo. Não é uma exibição da Globo.
- *South Park - O Filme* e *South Park: Bigger, Longer & Uncut* são o mesmo filme, citado com títulos diferentes em dois artigos.

A extração é heurística. **Confira o `trecho` antes de usar uma linha**, sobretudo as de confiança `media` e `baixa`: o ano pode se referir a outro fato da mesma frase.

Os trechos vêm da Wikipédia e estão sob a licença [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.pt_BR). A atribuição de cada trecho é o link na coluna `url`.

## Executar

```bash
pip install -e ".[dev,tv-filmes]"     # na raiz do repositório
python tv-filmes-1995-2005/src/run.py  # ~1 h na primeira vez; depois usa o cache
pytest -q tv-filmes-1995-2005
```

## Fontes avaliadas

| fonte | resultado |
|---|---|
| Wikipédia (pt), artigos | **usada**: é a fonte deste CSV |
| Wikipédia (pt), páginas das faixas | só listas de "mais exibidos": Sessão da Tarde 1974–1984 e Temperatura Máxima até 2017. Nenhuma recorta 1995–2005 |
| Wikidata | não registra exibições na TV de filmes estrangeiros. Só 74 itens têm Globo/SBT como emissora original, e são produções próprias |
| Filmow (listas de usuários) | bloqueia acesso automatizado (HTTP 403) |
| Hemeroteca Digital / *Jornal do Brasil* | tem o roteiro diário de 1995–2005 com busca por OCR, mas o leitor usa captcha e o material tem aviso de direito autoral (contato: CPDOC do JB). **Descartada para coleta automática** |
| Acervos Folha/Estadão | pagos; os termos não permitem coleta automática |
