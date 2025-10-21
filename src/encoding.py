from typing import List, Dict
from .utils import DAYS

def gene_space_from_config(cfg: dict) -> List[List[int]]:
    groups = cfg["groups"]
    descanso_idx = groups.index("Descanso")
    av = cfg.get("availability_minutes", {})
    space: List[List[int]] = []
    for d in DAYS:
        if av.get(d, 0) == 0:
            space.append([descanso_idx])              # si no hay disponibilidad, solo Descanso
        else:
            space.append(list(range(len(groups))))     # todos los grupos posibles
    return space

def decode(solution: List[int], cfg: dict) -> Dict[str, str]:
    groups = cfg["groups"]
    return {d: groups[int(g)] for d, g in zip(DAYS, solution)}
