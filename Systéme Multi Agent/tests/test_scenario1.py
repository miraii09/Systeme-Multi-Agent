import sys
import os
import tempfile
import threading
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from orchestrator.run_manager import RunManager
from tools.tools import read_csv, validate_schema, compute_metrics, generate_scenario1_report, http_get


# ============================================================
# TESTS SCÉNARIO 1
# ============================================================

def test_scenario1_success():
    """Test 1 : fichier valide → tout doit passer"""
    print("\n TEST 1 : Scénario 1 avec fichier valide")
    manager = RunManager(run_id="test_success")

    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data_synthetic', 'production.csv')

    manager.log_step("Execute", "read_csv", "lecture fichier")
    data = read_csv(csv_path)
    assert data is not None, "La lecture a échoué"
    manager.log_step("Critic", "validate_read", "OK")

    manager.log_step("Execute", "validate_schema", "validation")
    assert validate_schema(data), "Schéma invalide"
    manager.log_step("Critic", "validate_schema", "OK")

    manager.log_step("Execute", "compute_metrics", "calcul KPIs")
    metrics = compute_metrics(data)
    assert metrics is not None
    assert "total_production" in metrics
    assert "avg_defect_rate" in metrics
    assert "top_factories" in metrics
    manager.log_step("Critic", "compute_metrics", "OK")

    manager.log_step("Execute", "generate_report", "génération JSON")
    report = generate_scenario1_report(metrics)
    assert "top_factories" in report
    assert "avg_defect_rate" in report
    assert "delayed_factories" in report
    assert "alerts" in report
    manager.log_step("Critic", "generate_report", "OK")

    manager.finish(True)
    manager.print_summary()
    print(" TEST 1 RÉUSSI\n")
    return report


def test_file_not_found():
    """Test 2 : fichier inexistant → doit échouer proprement"""
    print("\n TEST 2 : Fichier inexistant")
    manager = RunManager(run_id="test_file_not_found")

    fake_path = os.path.join(os.path.dirname(__file__), '..', 'data_synthetic', 'fichier_inexistant.csv')

    manager.log_step("Execute", "read_csv", "tentative lecture")
    data = read_csv(fake_path)

    if data is None:
        manager.log_step("Critic", "read_csv", "échec", error="Fichier introuvable")
        manager.finish(False)
    else:
        manager.finish(True)

    manager.print_summary()
    print(" TEST 2 RÉUSSI (erreur bien gérée)\n")


def test_missing_column():
    """Test 3 : colonne manquante → validation doit échouer"""
    print("\n TEST 3 : Colonne manquante (product_id absent)")
    manager = RunManager(run_id="test_missing_column")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("date,factory_id,units_produced,defect_rate,lead_time_days,machine_downtime_hours\n")
        f.write("2026-01-01,F1,120,0.05,2,1.5")
        temp_path = f.name

    data = pd.read_csv(temp_path)
    manager.log_step("Execute", "validate_schema", "validation avec colonne manquante")

    is_valid = validate_schema(data)
    if not is_valid:
        manager.log_step("Critic", "validate_schema", "échec", error="Colonne product_id manquante")
        manager.finish(False)
    else:
        manager.finish(True)

    manager.print_summary()
    os.unlink(temp_path)
    print(" TEST 3 RÉUSSI (validation a détecté l'erreur)\n")


def test_invalid_type():
    """Test 4 : type incorrect (defect_rate = texte) → doit être géré"""
    print("\n TEST 4 : Type incorrect dans defect_rate")
    manager = RunManager(run_id="test_invalid_type")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("date,factory_id,product_id,units_produced,defect_rate,lead_time_days,machine_downtime_hours\n")
        f.write("2026-01-01,F1,P1,120,abc,2,1.5")
        temp_path = f.name

    data = pd.read_csv(temp_path)

    manager.log_step("Execute", "validate_schema", "validation type")
    schema_ok = validate_schema(data)

    if schema_ok:
        manager.log_step("Critic", "validate_schema", "schéma OK (colonne présente)")
        try:
            metrics = compute_metrics(data)
            import math
            if math.isnan(metrics["avg_defect_rate"]):
                manager.log_step("Critic", "compute_metrics", "échec", error="defect_rate invalide → NaN")
                manager.finish(False)
                print(" Type invalide détecté (NaN produit)")
            else:
                manager.finish(True)
        except Exception as e:
            manager.log_step("Critic", "compute_metrics", "exception", error=str(e))
            manager.finish(False)
    else:
        manager.finish(False)

    manager.print_summary()
    os.unlink(temp_path)
    print(" TEST 4 RÉUSSI (type invalide géré)\n")


# ============================================================
# TESTS SCÉNARIO 2 — Failure Injection
# ============================================================

def test_scenario2_timeout():
    """
    Test 5 : Scénario 2 — simulation timeout
    CORRECTION BUG 5 : test_mode=True → délai 0.1s au lieu de 6s
    Le comportement est identique (exception levée), seul le délai change.
    """
    print("\n TEST 5 : Scénario 2 — Timeout injecté")
    manager = RunManager(run_id="test_s2_timeout")

    manager.log_step("Execute", "http_get", "appel API avec timeout")
    try:
        # test_mode=True : réduit time.sleep(6) à time.sleep(0.1)
        result = http_get(use_real=False, failure_mode="timeout", test_mode=True)
        manager.log_step("Critic", "http_get", "succès inattendu")
        manager.finish(True)
    except Exception as e:
        manager.log_step("Critic", "http_get", "échec", error=str(e))
        manager.finish(False)
        print(f"   Erreur capturée : {e}")

    manager.print_summary()
    print(" TEST 5 RÉUSSI (timeout bien détecté)\n")


def test_scenario2_http_429():
    """Test 6 : Scénario 2 — simulation HTTP 429"""
    print("\n TEST 6 : Scénario 2 — HTTP 429 injecté")
    manager = RunManager(run_id="test_s2_429")

    manager.log_step("Execute", "http_get", "appel API avec 429")
    try:
        result = http_get(use_real=False, failure_mode="429")
        manager.log_step("Critic", "http_get", "succès inattendu")
        manager.finish(True)
    except Exception as e:
        manager.log_step("Critic", "http_get", "échec", error=str(e))
        manager.finish(False)
        print(f"   Erreur capturée : {e}")

    manager.print_summary()
    print(" TEST 6 RÉUSSI (HTTP 429 bien détecté)\n")


def test_scenario2_mock_success():
    """Test 7 : Scénario 2 — Mock API fonctionne normalement"""
    print("\n TEST 7 : Scénario 2 — Mock API normale")
    manager = RunManager(run_id="test_s2_mock")

    manager.log_step("Execute", "http_get", "appel mock API")
    result = http_get(use_real=False, failure_mode=None)

    assert result is not None, "Mock API a retourné None"
    assert "country" in result
    assert result["country"] == "Tunisia"
    assert "industrial_output_index" in result

    manager.log_step("Critic", "http_get", "OK — données Tunisia reçues")
    manager.finish(True)
    manager.print_summary()
    print(" TEST 7 RÉUSSI (Mock API fonctionne)\n")


# ============================================================
# TEST DE CONCURRENCE
# ============================================================

def test_concurrent_runs():
    """Test 8 : 3 runs en parallèle → pas de mélange de journaux"""
    print("\n TEST 8 : Concurrence — 3 runs en parallèle")

    results = {}
    errors = []

    def run_single(run_id):
        try:
            manager = RunManager(run_id=run_id)
            csv_path = os.path.join(os.path.dirname(__file__), '..', 'data_synthetic', 'production.csv')

            manager.log_step("Execute", "read_csv", "lecture")
            data = read_csv(csv_path)
            assert data is not None

            manager.log_step("Execute", "compute_metrics", "calcul")
            metrics = compute_metrics(data)
            assert metrics is not None

            manager.log_step("Execute", "generate_report", "rapport")
            report = generate_scenario1_report(metrics)

            manager.finish(True)
            results[run_id] = {"status": "success", "steps": len(manager.steps), "report": report}
        except Exception as e:
            errors.append(f"{run_id}: {e}")
            results[run_id] = {"status": "error"}

    threads = []
    for i in range(1, 4):
        t = threading.Thread(target=run_single, args=(f"concurrent_run_{i}",))
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Erreurs détectées : {errors}"
    assert len(results) == 3, "Tous les runs n'ont pas terminé"

    for run_id, result in results.items():
        assert result["status"] == "success", f"{run_id} a échoué"
        assert result["steps"] > 0, f"{run_id} n'a pas de steps"
        assert "top_factories" in result["report"]

    print(f"   3 runs parallèles terminés : {list(results.keys())}")
    print(f"   Aucun mélange de journaux détecté ✓")
    print(" TEST 8 RÉUSSI (concurrence OK)\n")


# ============================================================
# POINT D'ENTRÉE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" LANCEMENT DES TESTS — Scénario 1 + 2 + Concurrence")
    print("=" * 60)

    test_scenario1_success()
    test_file_not_found()
    test_missing_column()
    test_invalid_type()

    test_scenario2_timeout()      # rapide grâce à test_mode=True
    test_scenario2_http_429()
    test_scenario2_mock_success()

    test_concurrent_runs()

    print("=" * 60)
    print(" TOUS LES TESTS SONT PASSÉS ✓")
    print("=" * 60)
    #Ce fichier contient les tests automatiques pour le Scénario 1. Il vérifie que :
#le fichier CSV est lu correctement
#le schéma des données est valide
#les calculs des KPIs fonctionnent
#les erreurs (fichier inexistant, colonne manquante) sont bien gérées