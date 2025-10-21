import os, sys, csv, time, random
import numpy as np
import matplotlib.pyplot as plt
import pygad
import yaml

from .utils import load_yaml, project_path
from .encoding import gene_space_from_config, decode
from .fitness import make_fitness

def run(exp_path: str):
    cfg = load_yaml(project_path("src", "config.yaml"))
    exp = load_yaml(exp_path)

    # semilla
    seed = int(exp.get("random_seed", 0) or 0)
    if seed:
        random.seed(seed)
        np.random.seed(seed)

    gene_space = gene_space_from_config(cfg)

    # nuestra función de 2 parámetros
    fitness2 = make_fitness(cfg)

    # wrapper requerido por PyGAD 2.20.0 (3 parámetros)
    def fitness_func(ga_instance, solution, solution_idx):
        return fitness2(solution, solution_idx)

    population = int(exp["population"])
    generations = int(exp["generations"])
    crossover_prob = float(exp["crossover_prob"])
    mutation_prob = float(exp["mutation_prob"])

    parent_selection_type = "tournament" if exp["selection"] == "tournament" else "rws"
    params = dict(
        num_generations=generations,
        sol_per_pop=population,
        num_parents_mating=max(2, population // 2),
        num_genes=7,
        fitness_func=fitness_func,
        parent_selection_type=parent_selection_type,
        K_tournament=int(exp.get("tournament_k", 3)),
        crossover_type="single_point",
        crossover_probability=crossover_prob,
        mutation_type="random",
        mutation_probability=mutation_prob,
        gene_space=gene_space,
        gene_type=int,
        keep_parents=1,
        keep_elitism=1,
        allow_duplicate_genes=True
    )


    history_best = []
    history_avg = []

    def on_gen(ga):
        # mejor de la generación
        best_fit = ga.best_solution(pop_fitness=ga.last_generation_fitness)[1]
        history_best.append(float(best_fit))
        # promedio (recalculo para robustez) usando la versión de 2 parámetros
        fits = [fitness2(sol, idx) for idx, sol in enumerate(ga.population)]
        history_avg.append(float(np.mean(fits)))

    ga = pygad.GA(on_generation=on_gen, **params)
    ga.run()

    best_sol, best_fit, _ = ga.best_solution()
    best_names = decode(best_sol, cfg)

    # paths de salida
    exp_name = os.path.splitext(os.path.basename(exp_path))[0]
    out_dir = project_path("experiments", "logs")
    os.makedirs(out_dir, exist_ok=True)

    # CSV historia
    csv_path = os.path.join(out_dir, f"{exp_name}_history.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["generation", "best_fitness", "avg_fitness"])
        for i, (b, a) in enumerate(zip(history_best, history_avg), start=1):
            w.writerow([i, f"{b:.6f}", f"{a:.6f}"])

    # YAML mejor solución
    best_yaml = {
        "best_fitness": float(best_fit),
        "schedule": best_names
    }
    with open(os.path.join(out_dir, f"{exp_name}_best.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(best_yaml, f, allow_unicode=True, sort_keys=False)

    # Plot
    plt.figure()
    plt.plot(range(1, len(history_best)+1), history_best, label="Best")
    plt.plot(range(1, len(history_avg)+1), history_avg, label="Average")
    plt.xlabel("Generation"); plt.ylabel("Fitness"); plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f"{exp_name}_fitness.png"))
    plt.close()

    print("\n=== BEST SOLUTION ===")
    print(f"Fitness: {best_fit:.4f}")
    for d, g in best_names.items():
        print(f"{d}: {g}")
    print(f"\nArchivos guardados en: {out_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m src.runner experiments/exp1.yaml")
        sys.exit(1)
    run(sys.argv[1])

