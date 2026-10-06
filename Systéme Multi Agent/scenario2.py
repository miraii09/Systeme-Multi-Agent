import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# On ajoute le chemin de orchestrator pour utiliser agent_loop
sys.path.append(os.path.join(os.path.dirname(__file__), 'orchestrator'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'dp_cache'))

from agent_loop import run_agent_loop
from dp_cache import reset_cache, get_cache_stats, show_stats



# RUN NORMAL : API fonctionne normalement

def run_normal():
    print("\n" + "="*60)
    print("  RUN NORMAL — Scénario 2 (sans erreur)")
    print("="*60)
    
    # Reset cache avant run pour des stats propres
    reset_cache()
    
    report, journal, cache_stats = run_agent_loop(
        run_id="run_normal_scenario2",
        use_scenario2=True,
        inject_failure=None,
        reset_cache_before_run=False  # Déjà reset ci-dessus
    )
    
    # Afficher les stats du cache
    print("\n STATS CACHE (Run Normal):")
    print(f"   Compute Metrics - Hits: {cache_stats['compute']['hits']}, Misses: {cache_stats['compute']['misses']}, Ratio: {cache_stats['compute']['hit_ratio']}%")
    print(f"   Planner - Hits: {cache_stats['planner']['hits']}, Misses: {cache_stats['planner']['misses']}, Ratio: {cache_stats['planner']['hit_ratio']}%")
    
    return report, journal, cache_stats


# RUN AVEC ERREUR : API timeout → fallback Mock API


def run_with_error():
    print("\n" + "="*60)
    print("!!  RUN AVEC ERREUR — Scénario 2 (timeout injecté)")
    print("="*60)
    
    # Reset cache avant run
    reset_cache()
    
    report, journal, cache_stats = run_agent_loop(
        run_id="run_error_scenario2",
        use_scenario2=True,
        inject_failure="timeout",
        reset_cache_before_run=False
    )
    
    # Afficher les stats du cache
    print("\nSTATS CACHE (Run avec erreur):")
    print(f"   Compute Metrics - Hits: {cache_stats['compute']['hits']}, Misses: {cache_stats['compute']['misses']}, Ratio: {cache_stats['compute']['hit_ratio']}%")
    print(f"   Planner - Hits: {cache_stats['planner']['hits']}, Misses: {cache_stats['planner']['misses']}, Ratio: {cache_stats['planner']['hit_ratio']}%")
    
    return report, journal, cache_stats


# (OPTIONNEL) BENCHMARK POUR COMPARER BT vs BT+DP

def run_benchmark():
    """
    Compare les performances avec et sans cache sur le Scénario 2
    """
    import time
    
    print("\n" + "="*60)
    print("   BENCHMARK Scénario 2 : BT vs BT+DP")
    print("="*60)
    
    # === Test 1 : SANS cache (en désactivant le cache dans run_agent_loop) ===
    print("\nTest 1: Exécution SANS cache (Backtracking seul)")
    
    # Pour comparer, on peut faire un run avec reset après chaque étape
    # ou modifier temporairement le comportement. Ici on fait 2 runs et on moyenne
    
    times_no_cache = []
    for i in range(3):  # 3 runs pour moyenne
        reset_cache()
        start = time.time()
        report, journal, _ = run_agent_loop(
            run_id=f"benchmark_no_cache_{i}",
            use_scenario2=True,
            inject_failure=None,
            reset_cache_before_run=True
        )
        times_no_cache.append(time.time() - start)
    
    avg_no_cache = sum(times_no_cache) / len(times_no_cache)
    
    # === Test 2 : AVEC cache ===
    print("\nTest 2: Exécution AVEC cache (Backtracking + DP)")
    
    times_with_cache = []
    for i in range(3):
        reset_cache()
        start = time.time()
        report, journal, stats = run_agent_loop(
            run_id=f"benchmark_with_cache_{i}",
            use_scenario2=True,
            inject_failure=None,
            reset_cache_before_run=True
        )
        times_with_cache.append(time.time() - start)
    
    avg_with_cache = sum(times_with_cache) / len(times_with_cache)
    speedup = avg_no_cache / avg_with_cache if avg_with_cache > 0 else 0
    
    # === Résultats ===
    print("\n" + "="*60)
    print("   RÉSULTATS DU BENCHMARK")
    print("="*60)
    print(f"   Temps moyen sans cache  : {avg_no_cache:.3f} secondes")
    print(f"   Temps moyen avec cache  : {avg_with_cache:.3f} secondes")
    print(f"   Speedup              : x{speedup:.2f} plus rapide")
    
    # Afficher les stats finales
    final_stats = get_cache_stats()
    print(f"\n   Cache hit ratio (compute): {final_stats['compute']['hit_ratio']}%")
    print(f"   Cache hit ratio (planner): {final_stats['planner']['hit_ratio']}%")
    print("="*60)
    
    return {
        "avg_no_cache": avg_no_cache,
        "avg_with_cache": avg_with_cache,
        "speedup": speedup,
        "cache_stats": final_stats
    }



# POINT D'ENTRÉE


if __name__ == "__main__":
    print("\n" + "* "*15)
    print("   SCÉNARIO 2 — Système Multi-Agent Tunisie")
    print("   avec DP Memoization (Membre 3)")
    print("*"*30)

    # 1. Run normal
    print("\n📌 TEST 1: Run Normal")
    report_normal, journal_normal, stats_normal = run_normal()

    print("\n" + "-"*60)

    # 2. Run avec erreur injectée
    print("\n TEST 2: Run avec erreur (timeout)")
    report_error, journal_error, stats_error = run_with_error()
    
    print("\n" + "-"*60)
    
    # 3. (Optionnel) Benchmark
    print("\n TEST 3: Benchmark performance (optionnel)")
    print("   Tape 'y' pour lancer le benchmark (plus long) : ")
    # benchmark_results = run_benchmark()  # Décommenter pour activer

    # Résumé final
    print("\n" + "="*60)
    print(" ************ RÉSUMÉ FINAL *************")
    print("="*60)
    print(f"  Run Normal    → {'Succès' if report_normal else ' Échec'}")
    print(f"  Run Erreur    → {'Fallback utilisé' if report_error else 'Arrêt'}")
    
    print(f"\n STATISTIQUES CACHE (Run Normal):")
    print(f"     Compute Metrics : {stats_normal['compute']['hit_ratio']}% hit ratio ({stats_normal['compute']['hits']} hits / {stats_normal['compute']['total_calls']} calls)")
    print(f"     Planner         : {stats_normal['planner']['hit_ratio']}% hit ratio ({stats_normal['planner']['hits']} hits / {stats_normal['planner']['total_calls']} calls)")
    
    print("="*60)