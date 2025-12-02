import re


DEFAULT_KEYWORDS = {
    # keyword -> base minutes
    "enviar email": 10,
    "responder": 8,
    "pedir": 8,
    "llamar": 30,
    "reunion": 60,
    "leer": 20,
    "revisar": 45,
    "escribir": 60,
    "documento": 60,
    "estudiar": 90,
    "investigar": 90,
    "setup": 120,
    "configurar": 90,
    "probar": 45,
    "desplegar": 60,
    "arreglar": 45,
    "diseñar": 90,
    "planear": 45,
}

WORD_COUNT_THRESHOLD = 12
WORD_COUNT_BONUS = 15


class HeuristicEstimator:
    def __init__(self, keyword_table: dict[str, int] = None):
        self.keywords = keyword_table or DEFAULT_KEYWORDS

    def _text_scores(self, text: str):
        text_l = (text or "").lower()
        score = 0
        matches = []
        for kw, minutes in self.keywords.items():
            # word boundary match
            if re.search(rf"\\b{re.escape(kw)}\\b", text_l):
                score = max(score, minutes)
                matches.append(kw)
        # word count heuristic
        wc = len((text or "").split())
        if wc >= WORD_COUNT_THRESHOLD:
            score += WORD_COUNT_BONUS
        return score, matches, wc

    def estimate(self, task: object) -> dict[str, any]:
        """
        Returns: { 'estimated_minutes': int, 'reason': str, 'matches': list, 'word_count': int}
        """
        content = task.content or ""
        description = task.description or ""
        text_combined = f"{content} {description}".lower().strip()

        score, matches, wc = self._text_scores(text_combined)

        # If no match, return 0 so higher-level engine can fallback
        return {
            "estimated_minutes": int(score),
            "reason": "heuristic" if score > 0 else "no_match",
            "matches": matches,
            "word_count": wc,
        }
