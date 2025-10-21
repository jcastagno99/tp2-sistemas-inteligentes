from typing import List
from .utils import DAYS

def _diversity_score(solution_names: List[str], target_low: int, target_high: int) -> float:
    uniques = len(set(g for g in solution_names if g != "Descanso"))
    if uniques == 0:
        return 0.0
    if uniques < target_low:
        return max(0.0, uniques / max(1, target_low))
    if uniques > target_high:
        return max(0.0, 1.0 - (uniques - target_high) / max(1, target_high))
    return 1.0

def _rest_spacing_score(solution_names: List[str]) -> float:
    total_pairs, ok = 0, 0
    for i in range(len(solution_names) - 1):
        a, b = solution_names[i], solution_names[i + 1]
        if a == "Descanso" or b == "Descanso":
            continue
        total_pairs += 1
        if a != b:
            ok += 1
    return 1.0 if total_pairs == 0 else ok / total_pairs

def _availability_score(solution_names: List[str], availability: dict) -> float:
    ok, total = 0, 0
    for d, g in zip(DAYS, solution_names):
        if availability.get(d, 0) == 0:
            total += 1
            if g == "Descanso":
                ok += 1
    return 1.0 if total == 0 else ok / total

def _user_prefs_score(solution_names: List[str], prefs: dict) -> float:
    score = 0.0
    req = int(prefs.get("require_cardio_per_week", 0) or 0)
    if req <= 0:
        score += 0.5
    else:
        cardios = sum(1 for g in solution_names if g == "Cardio")
        score += 1.0 if cardios >= req else max(0.0, cardios / max(1, req))
    if prefs.get("legs_priority_bonus", 0) and any(g == "Piernas" for g in solution_names):
        score += float(prefs["legs_priority_bonus"])
    return min(1.0, score)

def make_fitness(cfg: dict):
    weights = cfg["fitness_weights"]
    groups = cfg["groups"]
    availability = cfg.get("availability_minutes", {})
    prefs = cfg.get("preferences", {})
    target_low, target_high = prefs.get("diversity_target_unique_groups", [4, 5])

    def fitness_func(solution, solution_idx) -> float:
        names = [groups[int(g)] for g in solution]
        diversity = _diversity_score(names, int(target_low), int(target_high))
        rest = _rest_spacing_score(names)
        avail = _availability_score(names, availability)
        up = _user_prefs_score(names, prefs)
        return (weights["diversity"] * diversity +
                weights["rest_spacing"] * rest +
                weights["availability"] * avail +
                weights["user_prefs"] * up)
    return fitness_func
