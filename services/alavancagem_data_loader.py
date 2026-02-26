import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class AlavancagemDataLoader:

    def __init__(self):
        self.conn_args = {
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASS"),
            "dbname": os.getenv("DB_NAME"),
            "sslmode": os.getenv("DB_SSLMODE", "require")
        }

    def _conn(self):
        return psycopg2.connect(**self.conn_args)

    # ---------------------------------------------------------
    # CARREGAR FIXTURE
    # ---------------------------------------------------------
    def load_fixture(self, fixture_id):
        conn = self._conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT fixture_id, league_id, season, home_team, away_team,
                   match_datetime, status, home_team_id, away_team_id
            FROM fixtures
            WHERE fixture_id = %s;
        """, (fixture_id,))

        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return None
        
        return {
            "fixture_id": row[0],
            "league_id": row[1],
            "season": row[2],
            "home_team": row[3],
            "away_team": row[4],
            "match_datetime": row[5].isoformat() if row[5] else None,
            "status": row[6],
            "home_team_id": row[7],
            "away_team_id": row[8]
        }

    # ---------------------------------------------------------
    # CARREGAR ODDS VALUES
    # ---------------------------------------------------------
    def load_odds_values(self, fixture_id):
        conn = self._conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT market_name, market_type, line_value, odd_value,
                   bookmaker_name, side_team, team_id, team_name
            FROM odds_values
            WHERE fixture_id = %s;
        """, (fixture_id,))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        odds = []
        for r in rows:
            odds.append({
                "market_name": r[0],
                "market_type": r[1],
                "line": r[2],
                "odd": float(r[3]),
                "bet_house": r[4],
                "side_team": r[5],
                "team_id": r[6],
                "team_name": r[7]
            })

        return odds

    # ---------------------------------------------------------
    # CARREGAR MERCADOS (DESCRIÇÃO)
    # ---------------------------------------------------------
    def load_markets(self, fixture_id):
        conn = self._conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT bet_name, market_pt
            FROM odds_markets
            WHERE fixture_id = %s;
        """, (fixture_id,))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        markets = []
        for r in rows:
            markets.append({
                "bet_name": r[0],
                "market_pt": r[1],
            })

        return markets

    # ---------------------------------------------------------
    # CARREGAR ESTATÍSTICAS HOME (context_type = 'home')
    # ---------------------------------------------------------
    def load_stats_home(self, home_team_id, league_id, season):
        conn = self._conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM team_statistics
            WHERE team_id = %s
              AND league_id = %s
              AND season = %s
              AND context_type = 'home';
        """, (home_team_id, league_id, season))

        row = cur.fetchone()
        desc = [d[0] for d in cur.description]

        cur.close()
        conn.close()

        if not row:
            return {}

        return dict(zip(desc, row))

    # ---------------------------------------------------------
    # CARREGAR ESTATÍSTICAS AWAY (context_type = 'away')
    # ---------------------------------------------------------
    def load_stats_away(self, away_team_id, league_id, season):
        conn = self._conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM team_statistics
            WHERE team_id = %s
              AND league_id = %s
              AND season = %s
              AND context_type = 'away';
        """, (away_team_id, league_id, season))

        row = cur.fetchone()
        desc = [d[0] for d in cur.description]

        cur.close()
        conn.close()

        if not row:
            return {}

        return dict(zip(desc, row))

    # ---------------------------------------------------------
    # CARREGAR TODOS OS JOGOS EM CASA
    # ---------------------------------------------------------
    def load_home_games(self, home_team_id):
        conn = self._conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM match_statistics
            WHERE home_team_id = %s
            ORDER BY match_date DESC;
        """, (home_team_id,))

        rows = cur.fetchall()
        desc = [d[0] for d in cur.description]

        cur.close()
        conn.close()

        return [dict(zip(desc, r)) for r in rows]

    # ---------------------------------------------------------
    # CARREGAR TODOS OS JOGOS FORA
    # ---------------------------------------------------------
    def load_away_games(self, away_team_id):
        conn = self._conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM match_statistics
            WHERE away_team_id = %s
            ORDER BY match_date DESC;
        """, (away_team_id,))

        rows = cur.fetchall()
        desc = [d[0] for d in cur.description]

        cur.close()
        conn.close()

        return [dict(zip(desc, r)) for r in rows]

    # ---------------------------------------------------------
    # MONTAR O PACOTE COMPLETO PARA A IA
    # ---------------------------------------------------------
    def build_package(self, fixture_id):

        fixture = self.load_fixture(fixture_id)
        if not fixture:
            return None

        odds_values = self.load_odds_values(fixture_id)
        odds_markets = self.load_markets(fixture_id)

        home_stats = self.load_stats_home(
            fixture["home_team_id"],
            fixture["league_id"],
            fixture["season"]
        )

        away_stats = self.load_stats_away(
            fixture["away_team_id"],
            fixture["league_id"],
            fixture["season"]
        )

        home_games = self.load_home_games(fixture["home_team_id"])
        away_games = self.load_away_games(fixture["away_team_id"])

        return {
            "fixture": fixture,
            "odds_values": odds_values,
            "odds_markets": odds_markets,
            "home_stats": home_stats,
            "away_stats": away_stats,
            "home_games": home_games,   # todos jogos em casa
            "away_games": away_games    # todos jogos fora
        }