import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AlavancagemAIService:

    def __init__(self):
        self.client = OpenAI()
        self.model = os.getenv("AI_MODEL_NAME")
        self.odd_min = float(os.getenv("ODD_MIN"))
        self.odd_max = float(os.getenv("ODD_MAX"))

    def build_prompt(self, dados_fixture, dados_odds, stats_home, stats_away):
        return f"""
Você é uma IA especialista em alavancagem 3X.

Objetivo:
- Odd final entre {self.odd_min} e {self.odd_max}
- Pode ser simples ou múltipla (máx 2 seleções)
- Priorize segurança, consistência e estatísticas estáveis

Formato:
{{
  "market": "",
  "market2": "",
  "line": "",
  "odd": "",
  "odd2": "",
  "bet_house": "",
  "confidence": 0,
  "reasoning": ""
}}
"""

    def generate(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Assistente IA Alavancagem 3X"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.10,
        )

        raw = response.choices[0].message.content
        try:
            return json.loads(raw)
        except:
            return None