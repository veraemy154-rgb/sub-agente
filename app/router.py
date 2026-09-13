"""Router de intencion: heuristico por defecto (0 tokens), LLM opcional despues."""
from .agents import AGENTS

def clasificar(texto: str) -> str:
    t = texto.lower()
    scores = {area: sum(1 for kw in cfg["keywords"] if kw in t) for area, cfg in AGENTS.items()}
    mejor = max(scores, key=scores.get)
    return mejor if scores[mejor] > 0 else "operaciones"
