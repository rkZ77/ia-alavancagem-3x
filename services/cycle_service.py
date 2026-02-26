import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class CycleService:

    def __init__(self):
        self.steps_required = int(os.getenv("ALAVANCAGEM_STEPS"))

    # -------------------------------------------------------
    # Conexão Supabase (SSL REQUIRED)
    # -------------------------------------------------------
    def _conn(self):
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            dbname=os.getenv("DB_NAME"),
            sslmode=os.getenv("DB_SSLMODE", "require")
        )

    # -------------------------------------------------------
    # BUSCA CICLO ATUAL (se não tiver fechado)
    # -------------------------------------------------------
    def get_current_cycle(self):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT cycle_id, etapa 
            FROM ia_alavancagem_cycles
            WHERE is_cycle_closed = FALSE
            ORDER BY id DESC
            LIMIT 1;
        """)
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return None
        
        return {"cycle_id": row[0], "etapa": row[1]}

    # -------------------------------------------------------
    # INICIA NOVO ciclo_id
    # -------------------------------------------------------
    def start_new_cycle(self):
        conn = self._conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT COALESCE(MAX(cycle_id), 0) + 1 FROM ia_alavancagem_cycles;
        """)
        new_cycle_id = cur.fetchone()[0]

        cur.close()
        conn.close()
        return new_cycle_id

    # -------------------------------------------------------
    # SALVA ETAPA
    # -------------------------------------------------------
    def save_step(self, cycle_id, etapa, suggestion):
        conn = self._conn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO ia_alavancagem_cycles (
                cycle_id, etapa, fixture_id, selections,
                odd, confidence, ev, reasoning, status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'PENDING')
        """,
        (
            cycle_id,
            etapa,
            suggestion["fixture_id"],
            suggestion["selections"],   # JSONB
            suggestion["odd"],
            suggestion["confidence"],
            suggestion["ev"],
            suggestion["reasoning"],
        ))

        conn.commit()
        cur.close()
        conn.close()

    # -------------------------------------------------------
    # REGISTRA GREEN / RED
    # -------------------------------------------------------
    def register_result(self, step_id, result):
        conn = self._conn()
        cur = conn.cursor()

        cur.execute("""
            UPDATE ia_alavancagem_cycles
            SET status = %s, closed_at = NOW()
            WHERE id = %s;
        """, (result, step_id))

        conn.commit()
        cur.close()
        conn.close()

    # -------------------------------------------------------
    # VERIFICA STATUS DO CICLO
    # -------------------------------------------------------
    def check_cycle_status(self, cycle_id):
        conn = self._conn()
        cur = conn.cursor()

        # Se teve 1 RED → ciclo fecha
        cur.execute("""
            SELECT COUNT(*) FROM ia_alavancagem_cycles
            WHERE cycle_id = %s AND status = 'RED';
        """, (cycle_id,))
        reds = cur.fetchone()[0]

        if reds > 0:
            cur.execute("""
                UPDATE ia_alavancagem_cycles
                SET is_cycle_closed = TRUE
                WHERE cycle_id = %s;
            """, (cycle_id,))
            conn.commit()
            cur.close()
            conn.close()
            return "closed_red"

        # Se completou as etapas = sucesso
        cur.execute("""
            SELECT COUNT(*) FROM ia_alavancagem_cycles
            WHERE cycle_id = %s AND status = 'GREEN';
        """, (cycle_id,))
        greens = cur.fetchone()[0]

        if greens >= self.steps_required:
            cur.execute("""
                UPDATE ia_alavancagem_cycles
                SET is_cycle_closed = TRUE
                WHERE cycle_id = %s;
            """, (cycle_id,))
            conn.commit()
            cur.close()
            conn.close()
            return "closed_green"

        cur.close()
        conn.close()
        return "open"