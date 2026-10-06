import sys
import os
import json
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# On ajoute les chemins
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dp_cache'))

from tools import read_csv, validate_schema, compute_metrics, http_get, generate_report, generate_scenario1_report
from dp_cache import (
    get_from_cache, save_to_cache, show_stats,
    get_plan_from_cache, save_plan_to_cache, reset_cache, get_cache_stats
)

# Paramètres principaux de la boucle
MAX_STEPS = 10
MAX_RETRY = 3
# PLANIFICATEUR AVEC CACHE DP

def planner(step_number, context, last_action_failed=False, last_action=None):
    """
    Le Planificateur décide la prochaine action
    Avec BACKTRACKING + CACHE DP
    """
    use_s2 = context.get("use_scenario2", False)
    # ÉTAPE 1 : Vérifier le cache planner AVANT de calculer
    cached_plan = get_plan_from_cache(step_number, use_s2, last_action_failed, last_action)
    if cached_plan:
        print(f"\n[PLANIFICATEUR - CACHE] Étape {step_number} → {cached_plan} (réutilisé)")
        return cached_plan
    # ÉTAPE 2 : Calcul normal (cache miss)
    print(f"\n[PLANIFICATEUR] Étape {step_number}")

    # BACKTRACKING : si read_csv a échoué
    if last_action_failed and last_action == "read_csv":
        print("Backtracking : read_csv a échoué → tentative avec chemin alternatif")
        plan = "read_csv_alt"

    # BACKTRACKING : si validate_schema a échoué
    elif last_action_failed and last_action == "validate_schema":
        print("Pruning : schéma invalide → arrêt")
        plan = "stop"

    # Plan normal
    elif step_number == 1:
        print("   Plan : lire le fichier CSV")
        plan = "read_csv"
    elif step_number == 2:
        print("   Plan : valider le schéma")
        plan = "validate_schema"
    elif step_number == 3:
        print("   Plan : calculer les KPIs")
        plan = "compute_metrics"
    elif step_number == 4:
        if use_s2:
            print("   Plan : appeler l'API (Scénario 2)")
            plan = "http_get"
        else:
            print("   Plan : générer rapport Scénario 1")
            plan = "generate_scenario1_report"
    elif step_number == 5:
        print("   Plan : générer rapport Scénario 2")
        plan = "generate_report"
    else:
        print("   → Plan : aucune action → STOP")
        plan = "stop"
    # ÉTAPE 3 : Sauvegarder dans le cache planner
    save_plan_to_cache(step_number, use_s2, last_action_failed, last_action, plan)
    
    return plan



# EXÉCUTEUR (avec cache pour compute_metrics)
def executor(action, context, retry_count=0):
    """
    L'Exécuteur exécute l'action décidée par le Planificateur
    """
    print(f"[EXECUTEUR] Action : {action} (essai {retry_count + 1})")

    try:
        # ---- Lire le fichier CSV (chemin normal) ----
        if action == "read_csv":
            path = os.path.join(
                os.path.dirname(__file__), '..', 'data_synthetic', 'production.csv'
            )
            data = read_csv(path)
            if data is None:
                return False, context
            context["data"] = data
            return True, context

        # ---- BACKTRACKING : Lire le fichier CSV (chemin alternatif) ----
        elif action == "read_csv_alt":
            path_alt = os.path.join(
                os.path.dirname(__file__), '..', 'data_synthetic', 'production_backup.csv'
            )
            print(f"Backtracking : tentative avec {path_alt}")
            data = read_csv(path_alt)
            if data is None:
                return False, context
            context["data"] = data
            print("Backtracking réussi !")
            return True, context

        # ---- Vérifier le schéma ----
        elif action == "validate_schema":
            if "data" not in context:
                print("Pas de données à valider !")
                return False, context
            is_valid = validate_schema(context["data"])
            if not is_valid:
                return False, context
            context["schema_valid"] = True
            return True, context

        # ---- Calculer les KPIs (AVEC CACHE) ----
        elif action == "compute_metrics":
            if "data" not in context:
                print("Pas de données pour calculer !")
                return False, context
            try:
                # Vérifier le cache AVANT de calculer
                cache_key = "compute_metrics_production.csv"
                cached = get_from_cache(cache_key)
                if cached is not None:
                    context["metrics"] = cached
                    return True, context

                # Pas dans le cache → calculer et sauvegarder
                metrics = compute_metrics(context["data"])
                save_to_cache(cache_key, metrics)
                context["metrics"] = metrics
                return True, context

            except Exception as e:
                print("Fallback : utilisation de métriques par défaut")
                context["metrics"] = {
                    "total_production": 0,
                    "avg_defect_rate": 0,
                    "avg_lead_time": 0,
                    "top_factories": [],
                    "delayed_factories": [],
                    "alerts": ["Fallback metrics utilisées"]
                }
                return True, context

        # ---- Appeler l'API ----
        elif action == "http_get":
            failure = context.get("inject_failure", None)
            try:
                api_data = http_get(use_real=False, failure_mode=failure)
            except Exception as e:
                print(f"   !! API échouée ({e}) → Fallback Mock API utilisé")
                context["fallback_used"] = True
                api_data = http_get(use_real=False, failure_mode=None)
            if api_data is None:
                return False, context
            context["api_data"] = api_data
            return True, context

        # ---- Générer rapport Scénario 2 ----
        elif action == "generate_report":
            if "metrics" not in context or "api_data" not in context:
                return False, context
            api_values = context["api_data"].get("industrial_output_index", [])
            report = generate_report(context["metrics"], api_values)
            context["report"] = report
            return True, context

        # ---- Générer rapport Scénario 1 ----
        elif action == "generate_scenario1_report":
            if "metrics" not in context:
                print("Données manquantes pour le rapport Scénario 1 !")
                return False, context
            report = generate_scenario1_report(context["metrics"])
            context["report"] = report
            print(f"Rapport Scénario 1 généré")
            return True, context

        else:
            print(f"Action inconnue : {action}")
            return False, context

    except Exception as e:
        print(f"Erreur inattendue : {e}")
        return False, context



# CRITIQUE (avec PRUNING)
def critic(action, success, context, retry_count):
    """
    Le Critique décide : continue, retry, ou stop
    Avec PRUNING : certaines erreurs sont fatales
    """
    print(f"[CRITIQUE] Action '{action}' → {'succès' if success else 'échec'}")

    # PRUNING : erreurs fatales
    if not success:
        fatal_errors = ["validate_schema", "generate_report", "generate_scenario1_report"]
        if action in fatal_errors:
            print(f"PRUNING : erreur fatale sur '{action}', arrêt immédiat")
            return "stop"

    # Si rapport généré avec succès → stop
    if action in ["generate_report", "generate_scenario1_report"] and success:
        print("   → Décision : STOP (mission accomplie)")
        return "stop"

    if success:
        print("   → Décision : CONTINUE")
        return "continue"
    else:
        print("   → Décision : RETRY")
        return "retry"


# SAUVEGARDE DU LOG

def save_log(run_id, report, journal, error_injected=None, cache_stats=None):
    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{run_id}_{timestamp}.json"
    filepath = os.path.join(logs_dir, filename)

    log_data = {
        "run_id": run_id,
        "timestamp": timestamp,
        "error_injected": error_injected,
        "journal": journal,
        "final_report": report,
        "cache_stats": cache_stats  # Ajout des stats cache
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=4, ensure_ascii=False)

    print(f"\nLog sauvegardé : {filename}")



# BOUCLE PRINCIPALE

def run_agent_loop(run_id="run_1", use_scenario2=False, inject_failure=None, reset_cache_before_run=True):
    """
    Boucle principale : Planner → Executor → Critic
    use_scenario2  = True/False → choisir le scénario
    inject_failure = None / "timeout" / "429" → injecter une erreur (M2)
    reset_cache_before_run = True → réinitialise le cache avant chaque run
    """
    # Réinitialiser le cache avant le run pour des stats propres
    if reset_cache_before_run:
        reset_cache()
    
    print(f"\n{'='*50}")
    print(f"DÉMARRAGE Agent Loop | run_id = {run_id}")
    print(f"Scénario : {'2 (avec API)' if use_scenario2 else '1 (CSV uniquement)'}")
    if inject_failure:
        print(f"!!  Erreur injectée : {inject_failure}")
    print(f"{'='*50}")

    context = {"use_scenario2": use_scenario2}
    context["inject_failure"] = inject_failure

    step = 1
    retry_count = 0
    last_action_failed = False
    last_action = None
    journal = []

    while step <= MAX_STEPS:

        action = planner(step, context, last_action_failed, last_action)

        if action == "stop":
            print("\n[BOUCLE] Planner dit STOP → fin normale")
            break

        success, context = executor(action, context, retry_count)
        decision = critic(action, success, context, retry_count)

        journal.append({
            "step_id": f"step_{step}",
            "action": action,
            "success": success,
            "decision": decision,
            "retry": retry_count
        })

        if decision == "stop":
            print(f"\n[BOUCLE] Mission accomplie en {step} étapes !")
            break

        elif decision == "continue":
            step += 1
            retry_count = 0
            last_action_failed = False
            last_action = None

        elif decision == "retry":
            retry_count += 1
            last_action_failed = True
            last_action = action

            if retry_count >= MAX_RETRY:
                print(f"\n[BOUCLE] Maximum tentatives atteint ({MAX_RETRY}) → FALLBACK")
                context["fallback"] = True
                journal.append({
                    "step_id": f"step_{step}_fallback",
                    "action": action,
                    "success": False,
                    "decision": "fallback",
                    "retry": retry_count
                })
                step += 1
                retry_count = 0
                last_action_failed = False
                last_action = None
            else:
                print(f"\n[BOUCLE] Nouvelle tentative ({retry_count}/{MAX_RETRY})")

    # Affichage du journal
    print(f"\n{'='*50}")
    print(f"JOURNAL DE RUN : {run_id}")
    print(f"{'='*50}")
    for entry in journal:
        status = "" if entry["success"] else ""
        print(f"  {status} {entry['step_id']} | {entry['action']} | {entry['decision']}")

    # Affichage du rapport final
    final_report = context.get("report", None)
    if final_report:
        print(f"\nRAPPORT FINAL :")
        for key, value in final_report.items():
            print(f"   {key} : {value}")
    else:
        print("\nAucun rapport généré")

    # Récupérer les stats du cache
    cache_stats = get_cache_stats()
    
    # Afficher les stats
    show_stats()
    
    # Sauvegarder le log avec les stats
    save_log(run_id, final_report, journal, error_injected=inject_failure, cache_stats=cache_stats)

    return final_report, journal, cache_stats


# TEST DIRECT

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TEST SCÉNARIO 1 AVEC CACHE DP")
    print("="*60)
    
    # Test Scénario 1
    report, journal, stats = run_agent_loop(
        run_id="test_scenario1",
        use_scenario2=False,
        inject_failure=None,
        reset_cache_before_run=True
    )
    
    print("\n" + "="*60)
    print("STATS FINALES POUR LA GUI:")
    print("="*60)
    print(f"   Compute Metrics : {stats['compute']['hit_ratio']}% hit ratio")
    print(f"   Planner         : {stats['planner']['hit_ratio']}% hit ratio")
    print("="*60)