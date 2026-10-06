## Title : Système Multi-Agent — Suivi de Production Industrielle en Tunisie

> **DS2 — Problem Solving Course | Institut Supérieur de Gestion de Tunis**
> Groupe :  Almia Nour · Ben Hamouda Fatma · Kbaier Takwa · Feki Eya


##  Description du projet

Ce projet implémente un **système multi-agent d'orchestration d'outils** appliqué à l'industrie manufacturière tunisienne. Il simule un tableau de bord industriel quotidien permettant de surveiller :

- La **performance des lignes de production** par usine
- Les **taux de défaut** et alertes qualité
- Les **retards logistiques** (lead time > 3 jours)
- Les **indicateurs macroéconomiques tunisiens** via API (réelle ou simulée)

Le système implémente trois agents distincts (**Planner → Executor → Critic**) avec backtracking, pruning, et mémoïsation DP, ainsi qu'une interface graphique Streamlit.

## Aperçu de l'interface
(docs/Capture_De_Partie_L'interface.png)

## Mon rôle
J'ai développé principalement l'interface Streamlit ('gui/App.py'), le cache de mémoïsation ('orchestrator/dp_cache.py') et le scénario 2 (API simulée, injection de pannes, repli automatique et rapport enrichi, workflows/scenario2.py). J'ai collaboré avec l'équipe sur le reste du projet : architecture de la boucle d'agents, scénario 1, outils et tests.

##  Structure du projet

```
DS2_PROB_SOLV/
│
├── data_synthetic/
│   ├── production.csv            # Dataset principal (9 lignes, 7 colonnes)
│   └── production_backup.csv     # Backup pour backtracking
│
├── orchestrator/
│   ├── agent_loop.py             # Boucle principale Planner→Executor→Critic
│   ├── run_manager.py            # Gestion des run_id, journaux, résumés
│   └── dp_cache.py               # Cache DP (mémoïsation compute_metrics + planner)
│
├── tools/
│   └── tools.py                  # Outils : read_csv, validate_schema, compute_metrics, http_get, generate_report
│
├── workflows/
│   ├── sceanrio1.py              # Scénario 1 (CSV local, avec backtracking)
│   └── scenario2.py              # Scénario 2 (API externe, avec DP benchmark)
│
├── gui/
│   ├── App.py                    # Interface Streamlit principale
│   └── console_demo.py           # Démo console (sans GUI)
│
├── tests/
│   └── test_scenario1.py         # Tests unitaires + concurrence + injection d'erreur
│
├── logs/                         # Journaux JSON générés automatiquement
│
├── main.py                       # Point d'entrée principal
└── settings.json                 # Configuration VS Code
```


##  Installation

### Prérequis

- Python 3.11+
- pip

### 1. Cloner / décompresser le projet

```bash
cd DS2_PROB_SOLV
```

### 2. Installer les dépendances

```bash
pip install pandas streamlit
```

> **Packages utilisés :** `pandas`, `streamlit`, `os`, `sys`, `json`, `re`, `threading`, `time`, `uuid`, `datetime`, `math`, `glob`, `tempfile`

---

##  Exécution

### Lancer l'interface graphique (Streamlit)

```bash
cd gui
streamlit run App.py
```

Puis ouvrir : [http://localhost:8501](http://localhost:8501)

### Lancer depuis le point d'entrée principal

```bash
python main.py
```

### Lancer le Scénario 1 directement

```bash
python workflows/sceanrio1.py
```

### Lancer le Scénario 2 directement

```bash
python workflows/scenario2.py
```

### Lancer les tests automatiques

```bash
python tests/test_scenario1.py
```

### Lancer la démo console

```bash
python gui/console_demo.py
```

---

##  Scénarios implémentés

### Scénario 1 — Dashboard industriel local (CSV)

| Étape | Action        | Description                                             |
|-------|---------------|---------------------------------------------------------|
| 1 - `read_csv`        | Lecture de `production.csv`                             |
| 2 - `validate_schema` | Vérification des 7 colonnes obligatoires                |
| 3 - `compute_metrics` | Calcul des KPIs (production, défauts, retards, alertes) |
| 4 - `generate_scenario1_report` | Rapport JSON final                            |

**Output JSON attendu :**
```json
{
  "top_factories": ["F3", "F1"],
  "avg_defect_rate": 0.064,
  "delayed_factories": ["F2"],
  "alerts": ["Factory F2 has high defect rate", "Factory F2 has excessive downtime"]
}
```

**Failure injection testée :**
- Fichier introuvable → backtracking vers `production_backup.csv`
- Colonne manquante → pruning (arrêt immédiat)
- Type incorrect (defect_rate = texte) → NaN détecté

### Scénario 2 — API macroéconomique Tunisie

| Étape | Action | Description |
|-------|--------|-------------|
| 1–3 | (idem S1) | CSV + validation + KPIs |
| 4 | `http_get` | Appel API World Bank / Mock |
| 5 | `generate_report` | Rapport JSON enrichi |

**Failure injection testée :**
- HTTP 429 (rate limit) → exception capturée + fallback mock
- Timeout → exception + fallback mock
- JSON invalide → exception capturée

---

##  Architecture Multi-Agent

```
Planner → décide la prochaine action
    ↓
Executor → exécute l'outil, valide input/output
    ↓
Critic → évalue le résultat → CONTINUE / RETRY / STOP
```

- **MAX_STEPS = 10** — borne sur les étapes
- **MAX_RETRY = 3** — borne sur les tentatives
- **Backtracking** — si `read_csv` échoue → `read_csv_alt` (backup)
- **Pruning** — si `validate_schema` échoue → arrêt immédiat (erreur fatale)

---

##  DP Mémoïsation (dp_cache.py)

Deux caches sont utilisés :

| Cache | Clé | Utilité |
|-------|-----|---------|
| `compute_metrics` | `"compute_metrics_production.csv"` | Évite de recalculer les KPIs si le même fichier est traité deux fois |
| `planner` | `(step, use_s2, last_failed, last_action)` | Mémoïse les décisions du Planner pour accélérer les runs répétés |

**Statistiques affichées dans la GUI :** hits, misses, hit ratio, comparatif BT seul vs BT+DP.

---

##  Tests automatiques (test_scenario1.py)

| Test | Description |
|------|-------------|
| Test 1 | Fichier valide → pipeline complet |
| Test 2 | Fichier inexistant → erreur gérée proprement |
| Test 3 | Colonne manquante → validation échoue |
| Test 4 | Type incorrect (defect_rate=texte) → NaN détecté |
| Test 5 | Scénario 2 — timeout API → exception capturée |
| Test 6 | Scénario 2 — HTTP 429 → exception capturée |
| Test 7 | Mock API normale → données Tunisia reçues |
| Test 8 | 3 runs en parallèle → aucun mélange de journaux |

---

## Interface GUI (Streamlit — App.py)

5 onglets disponibles :

| Onglet | Contenu |
|--------|---------|
|  Journal d'exécution | Timeline Plan→Act→Critic avec statut par étape |
|  Tool-Call Inspector | Détails de chaque outil (input, output, description) |
|  Rapport Final | KPIs visuels (métriques, alertes, graphique tendance) |
|  Cache DP & Métriques | Statistiques hits/misses + comparatif BT vs BT+DP |
|  Historique & Logs | Runs passés + logs JSON sauvegardés (redactés) |

**Sécurité :** chemins absolus, tokens, IPs masqués automatiquement (`[REDACTED_PATH]`, `[REDACTED_TOKEN]`, `[REDACTED_IP]`) avant affichage.

---

## Sécurité & Politiques

-  Redaction des données sensibles avant affichage
-  Allow-list des outils : `read_csv`, `validate_schema`, `compute_metrics`, `http_get`, `generate_report` uniquement
-  Borne MAX_STEPS = 10 (pas de boucle infinie)
-  Borne MAX_RETRY = 3 (pas de retry infini)
-  Journaux isolés par run (pas de fuite d'état entre runs parallèles)
-  API allow-listée : World Bank Tunisia / endpoint Mock uniquement

---

##  Métriques d'évaluation

| Métrique | Valeur observée |
|----------|----------------|
| Task success rate | 100% (S1 normal) |
| Tool grounding rate | 100% (schema validé) |
| Failure recovery rate | 100% (backtracking + fallback mock) |
| DP cache hit ratio (compute) | 0% au 1er run, 100% aux runs suivants |
| DP cache hit ratio (planner) | 0% au 1er run, élevé aux runs répétés |
| Concurrence (3 threads) |  Aucune fuite d'état |

---

##  Limitations connues

- Le cache DP est en mémoire vive (reset entre sessions Streamlit si page rechargée)
- La vraie API World Bank nécessite une connexion internet (sinon, utiliser le Mock)
- `scenario2.py` appelle `run_agent_loop` avec 3 valeurs de retour — s'assurer que `agent_loop.py` retourne bien `(report, journal, cache_stats)`
- Le planificateur est un système de règles déterministe : il n'y a pas de modèle de langage.

---

##  Groupe

| Membre | Rôle principal |
|--------|---------------|
| Ben Hamouda Fatma | Scénario 1 + tools.py |
| Kbaier Takwa | Orchestrateur + agent_loop |
| Almia Nour | DP Cache + Scénario 2 |
| Feki Eya | GUI Streamlit + Tests |

---

##  Deadline

**Soumission : 05/05/2026 à 23:59 sur Moodle**
Sessions de validation : 06/05/2026 et 07/05/2026