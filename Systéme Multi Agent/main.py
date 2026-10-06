import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'orchestrator'))

from agent_loop import run_agent_loop

if __name__ == "__main__":

    print("=" * 50)
    print("Système Multi-Agent – Industrie Tunisie ")
    print("=" * 50)

    # CORRECTION : run_agent_loop retourne 3 valeurs depuis la Semaine 3
    report, journal, cache_stats = run_agent_loop(run_id="run_1")

    # Affichage optionnel des stats cache
    print(f"\nCache compute hit ratio : {cache_stats['compute']['hit_ratio']}%")
    print(f"Cache planner hit ratio : {cache_stats['planner']['hit_ratio']}%")