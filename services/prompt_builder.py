import json

class PromptBuilder:

    def __init__(self, odd_min=1.45, odd_max=1.55):
        self.odd_min = odd_min
        self.odd_max = odd_max

    def build(self, pkg):
        """
        pkg = pacote completo do Data Loader:
        {
            fixture, odds_values, odds_markets,
            home_stats, away_stats,
            home_games, away_games
        }
        """

        fixture = json.dumps(pkg["fixture"], ensure_ascii=False)
        odds_values = json.dumps(pkg["odds_values"], ensure_ascii=False)
        odds_markets = json.dumps(pkg["odds_markets"], ensure_ascii=False)
        home_stats = json.dumps(pkg["home_stats"], ensure_ascii=False)
        away_stats = json.dumps(pkg["away_stats"], ensure_ascii=False)
        home_games = json.dumps(pkg["home_games"], ensure_ascii=False)
        away_games = json.dumps(pkg["away_games"], ensure_ascii=False)

        return f"""
Você é uma IA especialista em análise conservadora para **Alavancagem 3X**.

OBJETIVO:
- Retornar **somente 1 sugestão** por jogo.
- Odd final obrigatoriamente entre **{self.odd_min} e {self.odd_max}**.
- Se não existir simples dentro do range, tentar **múltipla de 2 seleções**.
- Evitar mercados instáveis.
- Evitar linhas com volatilidade alta.
- Não usar handicap asiático.
- Só usar mercados bem definidos e consistentes.

CONDIÇÕES:
1. Analisar mandante e visitante **somente com base no contexto correto**:
   - Mandante → jogos em casa
   - Visitante → jogos fora
   - Nunca misturar dados gerais (isso já foi filtrado para você)
2. Avaliação deve ser feita com:
   - estatísticas home
   - estatísticas away
   - histórico home_games
   - histórico away_games
   - odds_values (todas odds disponíveis)
   - odds_markets (descrições)
3. Múltipla só é permitida com:
   - no máximo 2 seleções
   - odd_final = odd1 * odd2 dentro do range {self.odd_min}–{self.odd_max}
4. Nunca sugerir mercados como:
   - PL (Player)
   - Handicap Asiático
   - Linhas flutuantes
   - Over/Under quebrado (ex: 1.75 / 2.25)
5. Só usar:
   - Over/Under .5 (0.5, 1.5, 2.5, 3.5 etc)
   - DC
   - BTTS em casos de alta consistência
   - Total goals do time com linha clara (ex: +0.5)

RETORNO (JSON):
{{
  "selections": [
    {{"market": "", "line": "", "odd": 0, "bet_house": ""}},
    {{"market": "", "line": "", "odd": 0, "bet_house": ""}}  # opcional para múltipla
  ],
  "final_odd": 0,
  "confidence": 0.0,
  "reasoning": "Justificativa objetiva com base estatística."
}}

AGORA OS DADOS PARA ANÁLISE:

[Fixture]
{fixture}

[Odds Values]
{odds_values}

[Odds Markets]
{odds_markets}

[Estatísticas Mandante]
{home_stats}

[Estatísticas Visitante]
{away_stats}

[Jogos em Casa do Mandante]
{home_games}

[Jogos Fora do Visitante]
{away_games}

Responda somente com JSON válido.
"""