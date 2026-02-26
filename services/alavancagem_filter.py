class AlavancagemFilter:

    def __init__(self, odd_min, odd_max):
        self.min = odd_min
        self.max = odd_max

    def validate(self, suggestion):
        odd1 = float(suggestion.get("odd", 0))
        odd2 = suggestion.get("odd2")

        # simples
        if not odd2:
            return self.min <= odd1 <= self.max

        # múltipla
        odd2 = float(odd2)
        final = odd1 * odd2

        suggestion["final_odd"] = round(final, 2)
        return self.min <= final <= self.max