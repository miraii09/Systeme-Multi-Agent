import time
import sys
import threading

_lock = threading.Lock()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# DP MEMOIZATION — Cache des résultats déjà calculés
# éviter de recalculer la même chose deux fois

# CACHE POUR COMPUTE_METRICS


_cache = {}
_total_calls = 0
_cache_hits = 0


def get_from_cache(key):
    """
    Cherche un résultat dans le cache (compute_metrics)
    - key    : clé unique (ex: "compute_metrics_production.csv")
    - retour : résultat si trouvé, None sinon
    """
    global _total_calls, _cache_hits

    _total_calls += 1

    if key in _cache:
        _cache_hits += 1
        print(f" [CACHE HIT] clé '{key}' trouvée → résultat réutilisé")
        return _cache[key]

    print(f"[CACHE MISS] clé '{key}' non trouvée → calcul nécessaire")
    return None


def save_to_cache(key, result):
    """
    Sauvegarde un résultat dans le cache (compute_metrics)
    """
    _cache[key] = result
    print(f"[CACHE SAVE] résultat sauvegardé sous '{key}'")


# CACHE POUR LE PLANNER (DP Memoization des décisions)


_plan_cache = {}
_plan_hits = 0
_plan_misses = 0


def get_plan_from_cache(step_number, use_scenario2, last_action_failed, last_action):
    """
    Cherche une décision de planner dans le cache.
    Clé = (step, use_scenario2, last_action_failed, last_action)
    """
    global _plan_hits, _plan_misses
    
    last_act = str(last_action) if last_action else "None"
    key = f"plan_{step_number}_{use_scenario2}_{last_action_failed}_{last_act}"
    
    if key in _plan_cache:
        _plan_hits += 1
        print(f"[PLAN CACHE HIT] step={step_number} → plan réutilisé")
        return _plan_cache[key]
    
    _plan_misses += 1
    print(f"[PLAN CACHE MISS] step={step_number} → calcul nécessaire")
    return None


def save_plan_to_cache(step_number, use_scenario2, last_action_failed, last_action, plan):
    """
    Sauvegarde une décision de planner dans le cache.
    """
    global _plan_cache
    
    last_act = str(last_action) if last_action else "None"
    key = f"plan_{step_number}_{use_scenario2}_{last_action_failed}_{last_act}"
    
    _plan_cache[key] = plan
    print(f"[PLAN CACHE SAVE] step={step_number} → '{plan}' sauvegardé")


def get_plan_cache_stats():
    """
    Retourne les statistiques du cache planner.
    """
    total = _plan_hits + _plan_misses
    ratio = (_plan_hits / total * 100) if total > 0 else 0
    return {
        "hits": _plan_hits,
        "misses": _plan_misses,
        "total": total,
        "hit_ratio": round(ratio, 1)
    }


# STATISTIQUES GLOBALES 

def get_cache_stats():
    """
    Retourne un dictionnaire avec toutes les stats pour la GUI.
    """
    compute_total = _total_calls
    compute_hit_ratio = (_cache_hits / compute_total * 100) if compute_total > 0 else 0
    
    plan_total = _plan_hits + _plan_misses
    plan_hit_ratio = (_plan_hits / plan_total * 100) if plan_total > 0 else 0
    
    return {
        "compute": {
            "total_calls": _total_calls,
            "hits": _cache_hits,
            "misses": _total_calls - _cache_hits,
            "hit_ratio": round(compute_hit_ratio, 1)
        },
        "planner": {
            "total_calls": plan_total,
            "hits": _plan_hits,
            "misses": _plan_misses,
            "hit_ratio": round(plan_hit_ratio, 1)
        },
        "cache_size": len(_cache),
        "plan_cache_size": len(_plan_cache)
    }

# AFFICHAGE DES STATISTIQUES


def show_stats():
    """
    Affiche les stats des DEUX caches (compute_metrics + planner)
    """
    print("\n" + "="*50)
    print("STATISTIQUES DP MEMOIZATION")
    print("="*50)
    
    # Stats Compute Metrics
    print("\nCompute Metrics Cache:")
    print(f"   Total appels    : {_total_calls}")
    print(f"   Cache hits      : {_cache_hits}")
    print(f"   Cache misses    : {_total_calls - _cache_hits}")
    if _total_calls > 0:
        ratio = (_cache_hits / _total_calls) * 100
        print(f"   Hit ratio       : {ratio:.1f}%")
    else:
        print(f"   Hit ratio       : 0%")
    
    # Stats Planner
    print("\nPlanner Cache:")
    total_plan = _plan_hits + _plan_misses
    print(f"   Total appels    : {total_plan}")
    print(f"   Cache hits      : {_plan_hits}")
    print(f"   Cache misses    : {_plan_misses}")
    if total_plan > 0:
        plan_ratio = (_plan_hits / total_plan) * 100
        print(f"   Hit ratio       : {plan_ratio:.1f}%")
    else:
        print(f"   Hit ratio       : 0%")
    
    print("="*50)


# RÉINITIALISATION


def reset_cache():
    """
    Vide le cache et remet les compteurs à zéro (compute + planner)
    """
    global _cache, _total_calls, _cache_hits
    global _plan_cache, _plan_hits, _plan_misses
    
    _cache = {}
    _total_calls = 0
    _cache_hits = 0
    
    _plan_cache = {}
    _plan_hits = 0
    _plan_misses = 0
    
    print("Cache réinitialisé (compute_metrics + planner)")

# DÉMONSTRATION LATENCY SPEEDUP

def demo_latency():
    """
    Démontre le gain de vitesse avec le cache
    Compare le temps de calcul sans cache vs avec cache
    """
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))
    from tools import read_csv, compute_metrics

    path = os.path.join(os.path.dirname(__file__), '..', 'data_synthetic', 'production.csv')

    print("\n" + "="*50)
    print("DÉMONSTRATION LATENCY SPEEDUP")
    print("="*50)

    # --- Sans cache : on calcule à chaque fois ---
    print("\nSans cache (2 appels) :")
    reset_cache()

    debut = time.time()
    data = read_csv(path)
    compute_metrics(data)
    compute_metrics(data)
    temps_sans_cache = time.time() - debut
    print(f"Temps total : {temps_sans_cache:.4f} secondes")

    # --- Avec cache : on calcule une seule fois ---
    print("\nAvec cache (2 appels) :")
    reset_cache()

    debut = time.time()
    data = read_csv(path)

    key = "compute_metrics_production.csv"
    result = get_from_cache(key)
    if result is None:
        result = compute_metrics(data)
        save_to_cache(key, result)

    result2 = get_from_cache(key)

    temps_avec_cache = time.time() - debut
    print(f"Temps total : {temps_avec_cache:.4f} secondes")

    # --- Résultat ---
    print("\n" + "="*50)
    print("RÉSULTAT LATENCY SPEEDUP")
    print("="*50)
    print(f"   Sans cache : {temps_sans_cache:.4f} sec")
    print(f"   Avec cache : {temps_avec_cache:.4f} sec")
    if temps_avec_cache > 0:
        speedup = temps_sans_cache / temps_avec_cache
        print(f" Speedup  : x{speedup:.2f} plus rapide")
    print("="*50)

    show_stats()


# TEST DIRECT
if __name__ == "__main__":
    demo_latency()