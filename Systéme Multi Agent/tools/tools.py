import pandas as pd

#lit les données du .csv et retourne les donnees
#بالدارجة: تعطيها مسار الملف → تقرأه → ترجعلك البيانات. إذا ما لقاتش الملف → ترجع None (يعني "والو")
def read_csv(path):
    try:
        data = pd.read_csv(path)
        print("Fichier chargé avec succès ")
        return data
    except:
        print("Erreur : fichier introuvable ")
        return None

#verfication du .csv contient les colonnes necessaires
#بالدارجة: تفحص البيانات — هل فيها كل الأعمدة اللي نحتاجوها؟ إذا عمود ناقص → ترجع False
def validate_schema(data):
    required_columns = [
        "date",
        "factory_id",
        "product_id",
        "units_produced",
        "defect_rate",
        "lead_time_days",
        "machine_downtime_hours"
    ]
    for col in required_columns:
        if col not in data.columns:
            print(f"Erreur : colonne manquante {col} ")
            return False
    print("Schéma valide ")
    return True



def compute_metrics(data):
    """
    Calcule tous les indicateurs pour le Scénario 1
    Retourne un dictionnaire avec :
    - total_production
    - avg_defect_rate
    - avg_lead_time
    - top_factories
    - delayed_factories
    - alerts
    """
    # === CALCULS ===
    # 1. Production totale
    total_production = data["units_produced"].sum()

    # 2. Taux de défaut moyen
    avg_defect_rate = data["defect_rate"].mean()
    
    # 3. Délai moyen (lead time)
    avg_lead_time = data["lead_time_days"].mean()
    
    # 4. Usines avec taux de défaut > 8%
    high_defect_factories = data[data["defect_rate"] > 0.08]["factory_id"].unique().tolist()
    
    # 5. Commandes en retard (lead_time > 3 jours)
    delayed = data[data["lead_time_days"] > 3]
    delayed_factories = delayed["factory_id"].unique().tolist()
    
    # 6. Analyse des pannes (pour les alertes)
    downtime_by_factory = data.groupby("factory_id")["machine_downtime_hours"].sum().to_dict()
    
    # 7. Usines les plus performantes (basé sur production)
    factory_prod = data.groupby("factory_id")["units_produced"].sum()
    top_factories = factory_prod.nlargest(2).index.tolist()
    
    # 8. Alertes
    alerts = []
    
    # Alerte 1 : défauts élevés
    for factory in high_defect_factories:
        alerts.append(f"Factory {factory} has high defect rate")
    
    # Alerte 2 : downtime excessif (> 5h total)
    for factory, downtime in downtime_by_factory.items():
        if downtime > 5:
            alerts.append(f"Factory {factory} has excessive downtime")

    return {
        "total_production": int(total_production),
        "avg_defect_rate": float(avg_defect_rate),
        "avg_lead_time": float(avg_lead_time),
        "top_factories": top_factories,
        "delayed_factories": delayed_factories,
        "alerts": alerts
    }



# une Vrai API ou Simpuler Fake API
def http_get(use_real=False, failure_mode=None, test_mode=False):
    """
    Appel API réel ou simulé.
 
    Paramètres :
    - use_real      : True = vraie API World Bank, False = Mock
    - failure_mode  : None | "timeout" | "429" | "invalid_json"
    - test_mode     : True = réduit le délai timeout à 0.1s (pour les tests automatiques)
                      False = délai réaliste de 6s (pour la démo)
    """
    # --- Injection d'erreur ---
    if failure_mode == "timeout":
        import time
        # CORRECTION BUG 5 : délai réduit en mode test pour ne pas bloquer la suite
        delay = 0.1 if test_mode else 6
        print(f"!! Simulation timeout API... (délai: {delay}s)")
        time.sleep(delay)
        raise Exception("Timeout : API ne répond pas")
 
    elif failure_mode == "429":
        print("!! Simulation HTTP 429 - Too Many Requests")
        raise Exception("HTTP 429 : Rate limit dépassé")
 
    elif failure_mode == "invalid_json":
        print("!! Simulation JSON invalide")
        raise Exception("JSON invalide reçu")
 
    # --- Appel réel ---
    if use_real:
        import requests
        print("Vraie API")
        url = "https://api.worldbank.org/v2/country/TUN/indicator/NV.IND.MANF.ZS?format=json"
        try:
            response = requests.get(url, timeout=5)
            return response.json()
        except:
            print("Erreur API")
            return None
 
    # --- Mock ---
    else:
        print("Mock API")
        return {
            "country": "Tunisia",
            "industrial_output_index": [100, 105, 102],
            "manufacturing_growth": [2.1, 3.4, 1.8]
        }
#Générer le rapport final JSON
#بالدارجة: تجمع كل النتائج في JSON واحد منظم — هذا هو التقرير النهائي


def generate_report(csv_kpis, api_values):
    report = {
        "total_production": int(csv_kpis["total_production"]),
        "avg_defect_rate": float(csv_kpis["avg_defect_rate"]),
        "avg_lead_time": float(csv_kpis["avg_lead_time"]),
        "industrial_trend": api_values[:5],
        "status": "OK"
    }
    return report

#test à supprimmer aprés
"""csv_data = read_csv("data_synthetic/production.csv")

if csv_data is not None and validate_schema(csv_data):
    metrics = compute_metrics(csv_data)
    print(metrics)
    api_data = http_get(use_real=True)
    series = api_data[1]
    values = [item['value'] for item in series if item['value'] is not None]
    print(values[:5])
    report = generate_report(metrics, values)
    print(report)"""


#hethy fonction car L’énoncé demande un JSON spécifique pour le Scénario 1 

def generate_scenario1_report(metrics):
    """
    Génère le rapport JSON exact pour le Scénario 1
    Format demandé par l'énoncé :
    {
        "top_factories": [],
        "avg_defect_rate": 0,
        "delayed_factories": [],
        "alerts": []
    }
    """
    
    # On vérifie que les clés existent (sécurité)
    top_factories = metrics.get("top_factories", [])
    avg_defect_rate = metrics.get("avg_defect_rate", 0)
    delayed_factories = metrics.get("delayed_factories", [])
    alerts = metrics.get("alerts", [])
    
    # Retourner le rapport EXACT comme demandé
    return {
        "top_factories": top_factories,
        "avg_defect_rate": round(avg_defect_rate, 3),  # Arrondi à 3 décimales
        "delayed_factories": delayed_factories,
        "alerts": alerts
    }

    