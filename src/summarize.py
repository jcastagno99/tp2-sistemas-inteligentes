import os, yaml, csv, glob
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGS = os.path.join(ROOT, "experiments", "logs")
CFG_PATH = os.path.join(ROOT, "src", "config.yaml")

DAYS = ["mon","tue","wed","thu","fri","sat","sun"]

def load_yaml(path:str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def diversity(schedule: Dict[str,str]) -> int:
    return len({g for g in schedule.values() if g != "Descanso"})

def rest_spacing_ok_ratio(schedule: Dict[str,str]) -> float:
    pairs, ok = 0, 0
    days = [schedule[d] for d in DAYS]
    for i in range(len(days)-1):
        a, b = days[i], days[i+1]
        if a == "Descanso" or b == "Descanso":
            continue
        pairs += 1
        if a != b:
            ok += 1
    return 1.0 if pairs == 0 else ok/pairs

def cardio_count(schedule: Dict[str,str]) -> int:
    return sum(1 for g in schedule.values() if g == "Cardio")

def has_legs(schedule: Dict[str,str]) -> bool:
    return any(g == "Piernas" for g in schedule.values())

def sunday_is_rest(schedule: Dict[str,str]) -> bool:
    return schedule.get("sun","") == "Descanso"

def read_history(exp_name: str):
    path = os.path.join(LOGS, f"{exp_name}_history.csv")
    gens, best, avg = [], [], []
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            g = int(row["generation"])
            b = float(row["best_fitness"])
            a = float(row["avg_fitness"])
            gens.append(g); best.append(b); avg.append(a)
    return np.array(gens), np.array(best), np.array(avg)

def main():
    cfg = load_yaml(CFG_PATH)
    best_files = sorted(glob.glob(os.path.join(LOGS, "exp*_best.yaml")))
    exps = [os.path.basename(f).replace("_best.yaml","") for f in best_files]

    out_csv = os.path.join(LOGS, "summary.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "exp","best_fitness","gen_to_opt","avg_last","avg_std",
            "diversity","rest_ok_ratio","cardio_count","has_legs","sunday_rest"
        ])
        for exp in exps:
            best = load_yaml(os.path.join(LOGS, f"{exp}_best.yaml"))
            sched = best["schedule"]

            gens, best_hist, avg_hist = read_history(exp)
            # primera gen donde best >= 0.999
            hit = np.where(best_hist >= 0.999)[0]
            gen_to_opt = int(gens[hit[0]]) if hit.size > 0 else int(gens[-1])

            w.writerow([
                exp,
                f'{best["best_fitness"]:.6f}',
                gen_to_opt,
                f'{avg_hist[-1]:.4f}',
                f'{np.std(avg_hist):.4f}',
                diversity(sched),
                f'{rest_spacing_ok_ratio(sched):.4f}',
                cardio_count(sched),
                "yes" if has_legs(sched) else "no",
                "yes" if sunday_is_rest(sched) else "no",
            ])
