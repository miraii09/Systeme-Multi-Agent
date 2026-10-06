
# SCÉNARIO 1 - Dashboard industriel Tunisie
# Avec BACKTRACKING et PRUNING


import sys
import os

# Ajouter les chemins
sys.path.append(os.path.join(os.path.dirname(__file__), 'orchestrator'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from tools import read_csv, validate_schema, compute_metrics, generate_scenario1_report


def run_scenario1_normal(csv_path):
    """
    Exécution NORMALE du Scénario 1
    """
    print("\n" + "=" * 60)
    print("SCÉNARIO 1 - EXÉCUTION NORMALE")
    print("=" * 60)
    
    print("\n[1] Lecture du fichier CSV...")
    data = read_csv(csv_path)
    if data is None:
        print("Échec : fichier non trouvé")
        return None
    
    print("\n[2] Validation du schéma...")
    if not validate_schema(data):
        print("Échec : schéma invalide")
        return None
    
    print("\n[3] Calcul des indicateurs...")
    metrics = compute_metrics(data)
    
    print("\n[4] Génération du rapport JSON...")
    report = generate_scenario1_report(metrics)
    
    print("\n" + "=" * 60)
    print("RAPPORT FINAL")
    print("=" * 60)
    for key, value in report.items():
        print(f"   {key}: {value}")
    
    return report


def run_scenario1_with_backtracking(csv_path, backup_path):
    """
    Exécution avec BACKTRACKING
    Essaie le fichier principal, si échec → essaie le backup
    """
    print("\n" + "=" * 60)
    print("SCÉNARIO 1 - AVEC BACKTRACKING")
    print("=" * 60)
    
    print(f"\n[1] Tentative fichier principal : {csv_path}")
    data = read_csv(csv_path)
    
    if data is None and backup_path:
        print(f"\nBACKTRACKING : essai du fichier backup")
        print(f"   → {backup_path}")
        data = read_csv(backup_path)
        if data is not None:
            print("Backtracking réussi !")
    
    if data is None:
        print("\nÉchec total")
        return None
    
    print("\n[2] Validation du schéma...")
    if not validate_schema(data):
        print("PRUNING : schéma invalide → arrêt")
        return None
    
    print("\n[3] Calcul des indicateurs...")
    metrics = compute_metrics(data)
    
    print("\n[4] Génération du rapport...")
    report = generate_scenario1_report(metrics)
    
    print("\n" + "=" * 60)
    print("RAPPORT FINAL")
    print("=" * 60)
    for key, value in report.items():
        print(f"   {key}: {value}")
    
    return report


def run_scenario1_with_error_injection():
    """
    Injection d'erreur : fichier inexistant
    """
    print("\n" + "=" * 60)
    print("SCÉNARIO 1 - INJECTION D'ERREUR")
    print("=" * 60)
    
    fake_path = os.path.join(os.path.dirname(__file__), 'data_synthetic', 'fichier_inexistant.csv')
    print(f"\n[1] Tentative lecture : {fake_path}")
    data = read_csv(fake_path)
    
    if data is None:
        print("\nERREUR BIEN GÉRÉE")
        print(" → Fichier non trouvé, retourne None")
        return None
    
    return None



# MAIN


if __name__ == "__main__":
    
    csv_path = os.path.join(os.path.dirname(__file__), 'data_synthetic', 'production.csv')
    backup_path = os.path.join(os.path.dirname(__file__), 'data_synthetic', 'production_backup.csv')
    
    # Créer un backup si nécessaire
    if not os.path.exists(backup_path) and os.path.exists(csv_path):
        import shutil
        shutil.copy(csv_path, backup_path)
        print(f"Backup créé : {backup_path}")
    
    # TEST 1 : Normal
    run_scenario1_normal(csv_path)
    
    # TEST 2 : Injection d'erreur
    run_scenario1_with_error_injection()
    
    # TEST 3 : Backtracking (fichier principal inexistant)
    fake_path = os.path.join(os.path.dirname(__file__), 'data_synthetic', 'fichier_fake.csv')
    run_scenario1_with_backtracking(fake_path, csv_path)
    
    print("\n" + "=" * 60)
    print("FIN DES TESTS")
    print("=" * 60)