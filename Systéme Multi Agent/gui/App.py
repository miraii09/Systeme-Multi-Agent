import sys
import os
import glob
import json
import re
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'orchestrator'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dp_cache'))

from agent_loop import run_agent_loop

# ==============================
# CONFIGURATION PAGE
# ==============================
st.set_page_config(
    page_title="Tunisie Industrie — Multi-Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# STYLES CSS — Palette Beige / Rose Doux
# ==============================
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Lato:wght@300;400;700&family=Playfair+Display:wght@700&display=swap');

/* ── Variables de couleur ── */
:root {
    --beige-clair:   #FAF3EC;
    --beige-moyen:   #EFE3D4;
    --beige-fonce:   #D9C4AC;
    --rose-pale:     #F2D4D7;
    --rose-moyen:    #E8B4BA;
    --rose-accent:   #C8737C;
    --rose-fonce:    #A3515A;
    --brun-texte:    #5C3D35;
    --brun-doux:     #8B6057;
    --blanc:         #FDFAF7;
    --brown:        #3C1006;
    --black:        #000000;
}

/* ── Fond global ── */
.stApp {
    background: linear-gradient(135deg, var(--beige-clair) 0%, var(--rose-pale) 50%, var(--beige-moyen) 100%);
    font-family: 'Lato', sans-serif;
    color: var(--brun-texte);
}

/* ── Titre principal centré ── */
.titre-principal {
    text-align: center;
    font-family: 'Montserrat', 'Playfair Display', Georgia, serif !important;
    font-size: 5rem !important;
    font-weight: 700;
    color: var(--rose-fonce);
    letter-spacing: 0.04em;
    padding: 1.2rem 0 0.4rem 0;
    text-shadow: 1px 2px 8px rgba(163, 81, 90, 0.13);
    border-bottom: 2.5px solid var(--rose-moyen);
    margin-bottom: 0.5rem;
}

/* ── Sous-titre centré ── */
.sous-titre {
    text-align: center;
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.15rem;
    font-weight: 400;
    color: var(--brown);
    letter-spacing: 0.12em;
    margin-bottom: 1.5rem;
    font-style: italic;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--brown) 0%,var(--rose-accent) 0% ,var(--rose-pale) 100%) !important;
    border-right: 2px solid var(--rose-moyen);
}
[data-testid="stSidebar"] * {
    color: var(--brun-texte) !important;
    font-family: 'Lato', sans-serif;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-family: 'Cormorant Garamond', serif !important;
    color: var(--rose-fonce) !important;
}

/* ── Bouton principal ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--rose-accent), var(--rose-fonce)) !important;
    color: var(--blanc) !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Lato', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.2rem !important;
    box-shadow: 0 4px 14px rgba(163, 81, 90, 0.25) !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, var(--rose-fonce), var(--rose-accent)) !important;
    box-shadow: 0 6px 20px rgba(163, 81, 90, 0.35) !important;
    transform: translateY(-1px) !important;
}

/* ── Bouton secondaire ── */
.stButton > button {
    background: var(--beige-moyen) !important;
    color: var(--brun-texte) !important;
    border: 1.5px solid var(--rose-moyen) !important;
    border-radius: 8px !important;
    font-family: 'Lato', sans-serif !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] button {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: var(--balck) !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 0.5rem 1.1rem !important;
    background: var(--beige-moyen) !important;
    border: 1px solid var(--beige-fonce) !important;
    transition: all 0.18s !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    background: var(--rose-pale) !important;
    color: var(--rose-fonce) !important;
    border-bottom: 2.5px solid var(--rose-accent) !important;
    font-weight: 700 !important;
}

/* ── Métriques ── */
[data-testid="stMetric"] {
    background: var(--blanc) !important;
    border-radius: 12px !important;
    padding: 0.8rem 1rem !important;
    border: 1px solid var(--rose-pale) !important;
    box-shadow: 0 2px 10px rgba(200, 115, 124, 0.1) !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Lato', sans-serif !important;
    font-size: 0.8rem !important;
    color: var(--brown) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.7rem !important;
    color: var(--rose-fonce) !important;
    font-weight: 700 !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: var(--blanc) !important;
    border: 1px solid var(--beige-fonce) !important;
    border-radius: 10px !important;
    margin-bottom: 0.5rem !important;
    box-shadow: 0 1px 6px rgba(163, 81, 90, 0.07) !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Lato', sans-serif !important;
    font-weight: 600 !important;
    color: var(--brown) !important;
}

/* ── Info / Success / Warning / Error boxes ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'Lato', sans-serif !important;
}

/* ── Subheaders ── */
h2, h3 {
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    color: var(--rose-fonce) !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
}

/* ── Divider ── */
hr {
    border-color: var(--rose-moyen) !important;
    opacity: 0.5 !important;
}

/* ── Selectbox / Radio ── */
[data-testid="stSelectbox"] > div,
[data-testid="stRadio"] > div {
    background: var(--blanc) !important;
    border-radius: 8px !important;
    border: 1px solid var(--beige-fonce) !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    border: 1px solid var(--rose-pale) !important;
    overflow: hidden !important;
}

/* ── Code blocks ── */
code, pre {
    background: var(--beige-moyen) !important;
    color: var(--rose-fonce) !important;
    border-radius: 6px !important;
    font-size: 0.85rem !important;
}

/* ── Caption ── */
[data-testid="stCaptionContainer"] {
    color: var(--brun-doux) !important;
    font-style: italic !important;
    font-family: 'Cormorant Garamond', serif !important;
}

/* ── Toggle ── */
[data-testid="stToggle"] {
    accent-color: var(--rose-accent) !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    color: var(--rose-accent) !important;
}

/* ── Bandeau info en haut ── */
.info-bandeau {
    background: linear-gradient(90deg, var(--beige-moyen), var(--rose-pale));
    border-radius: 12px;
    padding: 0.6rem 1.4rem;
    border: 1px solid var(--rose-moyen);
    font-family: 'Lato', sans-serif;
    color: var(--brun-texte);
    font-size: 0.95rem;
    text-align: center;
    margin-bottom: 1rem;
}
            /* ── Caption — remplace le gris Streamlit par défaut ── */
[data-testid="stCaptionContainer"] p {
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    font-size: 1.05rem !important;
    font-style: italic !important;
    color: var(--brown)!important;
    letter-spacing: 0.06em !important;
}
</style>
""", unsafe_allow_html=True)


# ==============================
# REDACTION — données sensibles
# ==============================
def redact_sensitive(text):
    if not isinstance(text, str):
        text = str(text)
    text = re.sub(r'[A-Za-z]:\\[^\s\'"]+', '[REDACTED_PATH]', text)
    text = re.sub(r'/home/[^\s\'"]+', '[REDACTED_PATH]', text)
    text = re.sub(r'/mnt/[^\s\'"]+', '[REDACTED_PATH]', text)
    text = re.sub(r'\b[A-Za-z0-9]{32,}\b', '[REDACTED_TOKEN]', text)
    text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[REDACTED_IP]', text)
    return text


# ==============================
# TOOL DESCRIPTIONS
# ==============================
TOOL_DESCRIPTIONS = {
    "read_csv": {
        "description": "Lit le fichier CSV de production industrielle",
        "input": "data_synthetic/production.csv",
        "output_type": "DataFrame pandas (colonnes: date, factory_id, product_id...)"
    },
    "read_csv_alt": {
        "description": "Lecture fichier backup (déclenché par backtracking)",
        "input": "data_synthetic/production_backup.csv",
        "output_type": "DataFrame pandas"
    },
    "validate_schema": {
        "description": "Vérifie que les 7 colonnes obligatoires sont présentes",
        "input": "DataFrame — colonnes requises : date, factory_id, product_id, units_produced, defect_rate, lead_time_days, machine_downtime_hours",
        "output_type": "Boolean (True = valide, False = colonne manquante)"
    },
    "compute_metrics": {
        "description": "Calcule tous les KPIs (production, défauts, retards, alertes)",
        "input": "DataFrame validé",
        "output_type": "Dict JSON — total_production, avg_defect_rate, top_factories, delayed_factories, alerts"
    },
    "http_get": {
        "description": "Appel API externe Tunisia (World Bank / Mock)",
        "input": "URL allow-listée ou endpoint Mock Tunisia",
        "output_type": "JSON — country, industrial_output_index, manufacturing_growth"
    },
    "generate_scenario1_report": {
        "description": "Génère le rapport JSON final pour le Scénario 1",
        "input": "Métriques calculées par compute_metrics",
        "output_type": "JSON — top_factories, avg_defect_rate, delayed_factories, alerts"
    },
    "generate_report": {
        "description": "Génère le rapport JSON final pour le Scénario 2",
        "input": "Métriques CSV + données API",
        "output_type": "JSON — total_production, industrial_trend, status"
    }
}


# ==============================
# SESSION STATE
# ==============================
for key, default in {
    "run_triggered": False,
    "scenario": 1,
    "inject_failure": None,
    "report": None,
    "journal": [],
    "cache_stats": None,
    "run_history": []
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ==============================
# SIDEBAR
# ==============================
with st.sidebar:
    st.markdown("-> Contrôles <-")
    st.divider()

    st.markdown("--- Scénario ---")
    scenario_choice = st.radio(
        "Choisir le scénario :",
        options=[1, 2],
        format_func=lambda x: f"Scénario {x} — {'CSV local' if x == 1 else 'API externe'}",
        index=0
    )
    st.session_state.scenario = scenario_choice

    st.divider()

    st.markdown("--- Failure Injection ---")
    st.caption("Simule des erreurs pour tester la robustesse")

    failure_option = st.selectbox(
        "Type d'erreur :",
        options=["Aucune", "timeout", "429", "invalid_json"],
        index=0,
        help="timeout = API ne répond pas | 429 = rate limit | invalid_json = réponse corrompue"
    )
    st.session_state.inject_failure = None if failure_option == "Aucune" else failure_option

    if st.session_state.inject_failure:
        st.warning(f"Erreur activée : **{st.session_state.inject_failure}**")
    else:
        st.success(" Mode normal")

    st.divider()

    if st.button("▶️ Lancer le Scénario", use_container_width=True, type="primary"):
        st.session_state.run_triggered = True

    st.divider()
    st.caption(" DS2 — Système Multi-Agent\nIndustrie Tunisie 🇹🇳")
    st.caption("Agents : Planner · Executor · Critic")


# ==============================
# TITRE PRINCIPAL CENTRÉ
# ==============================
st.markdown(
    '<h1 class="titre-principal"> Système Multi-Agent — Suivi Production Industrielle en Tunisie</h1>',
    unsafe_allow_html=True
)
st.markdown(
    '<p class="sous-titre">Planner · Executor · Critic &nbsp;|&nbsp; Backtracking · DP Memoization · Failure Recovery</p>',
    unsafe_allow_html=True
)

# Bandeau d'état
col_i1, col_i2, col_i3 = st.columns(3)
col_i1.info(f" Scénario : **{st.session_state.scenario}**")
col_i2.info(f" Failure : **{st.session_state.inject_failure or 'aucune'}**")
col_i3.info(f" Runs : **{len(st.session_state.run_history)}**")
st.divider()


# ==============================
# EXÉCUTION
# ==============================
if st.session_state.run_triggered:
    with st.spinner("⏳ Agents en cours... (Planner → Executor → Critic)"):
        try:
            use_s2 = (st.session_state.scenario == 2)
            failure_str = st.session_state.inject_failure or "normal"
            run_id = f"streamlit_s{st.session_state.scenario}_{failure_str}"

            report, journal, cache_stats = run_agent_loop(
                run_id=run_id,
                use_scenario2=use_s2,
                inject_failure=st.session_state.inject_failure,
                reset_cache_before_run=True
            )

            st.session_state.report = report
            st.session_state.journal = journal
            st.session_state.cache_stats = cache_stats

            success = report is not None
            st.session_state.run_history.append({
                "run_id": run_id,
                "scénario": st.session_state.scenario,
                "failure": st.session_state.inject_failure or "—",
                "étapes": len(journal),
                "statut": "✅ Succès" if success else "❌ Échec",
                "cache_ratio": f"{cache_stats['compute']['hit_ratio']}%" if cache_stats else "—"
            })

            if success:
                st.success(f"✅ Exécution terminée en **{len(journal)} étapes** !")
            else:
                st.error("❌ Exécution terminée sans rapport (erreur gérée proprement)")

        except Exception as e:
            st.error(f"❌ Erreur : {redact_sensitive(str(e))}")

    st.session_state.run_triggered = False


# ==============================
# TABS
# ==============================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Journal d'exécution",
    "🔍 Tool-Call Inspector",
    "📊 Rapport & KPIs",
    "⚡ Cache DP & Métriques",
    "🕐 Historique & Logs"
])


# ==============================
# TAB 1 — Journal
# ==============================
with tab1:
    st.subheader("📋 Journal d'exécution")
    st.caption("Chaque étape : décision du Planner → action de l'Executor → verdict du Critic")

    if st.session_state.journal:
        total = len(st.session_state.journal)
        success_count = sum(1 for e in st.session_state.journal if e.get("success"))
        fail_count = total - success_count

        m1, m2, m3 = st.columns(3)
        m1.metric("Total étapes", total)
        m2.metric("✅ Succès", success_count)
        m3.metric("❌ Échecs", fail_count)

        st.divider()

        for entry in st.session_state.journal:
            success  = entry.get("success", False)
            decision = entry.get("decision", "")
            action   = entry.get("action", "")
            step_id  = entry.get("step_id", "")
            retry    = entry.get("retry", 0)

            if success and decision == "stop":
                icon, label = "🟢", "TERMINÉ"
            elif success:
                icon, label = "✅", "OK"
            elif decision == "fallback":
                icon, label = "🔄", "FALLBACK"
            elif decision == "retry":
                icon, label = "🔁", "RETRY"
            else:
                icon, label = "❌", "ÉCHEC"

            with st.expander(
                f"{icon} **{step_id}** — `{action}` → *{decision}* [{label}]",
                expanded=(decision == "stop" or not success)
            ):
                ca, cb, cc = st.columns(3)
                ca.markdown(f"** Planner**\nAction choisie : `{action}`")
                cb.markdown(f"** Executor**\nRésultat : {'✅ Succès' if success else '❌ Échec'}")
                cc.markdown(f"** Critic**\nDécision : `{decision}` | Tentative : {retry + 1}")
    else:
        st.info("! Aucun journal  — lancez un scénario.")


# ==============================
# TAB 2 — Tool-Call Inspector
# ==============================
with tab2:
    st.subheader("🔍 Tool-Call Inspector")
    st.caption("Détail de chaque outil : arguments d'entrée, validation schéma, statut, résultat.")

    if st.session_state.journal:
        show_redacted = st.toggle("🔒 Redaction des données sensibles", value=True)
        st.divider()

        for entry in st.session_state.journal:
            action   = entry.get("action", "")
            success  = entry.get("success", False)
            decision = entry.get("decision", "")
            step_id  = entry.get("step_id", "")
            retry    = entry.get("retry", 0)

            tool_info = TOOL_DESCRIPTIONS.get(action, {
                "description": "Outil non documenté",
                "input": "Inconnu",
                "output_type": "Inconnu"
            })

            status_badge = "✅" if success else "❌"

            with st.expander(f"{status_badge} **{step_id}** — Tool : `{action}`", expanded=False):
                col_left, col_right = st.columns(2)

                with col_left:
                    st.markdown("**📥 Input**")
                    input_display = tool_info["input"]
                    if show_redacted:
                        input_display = redact_sensitive(input_display)
                    st.code(input_display, language="text")
                    st.markdown("**📖 Description**")
                    st.write(tool_info["description"])

                with col_right:
                    st.markdown("**📤 Output type**")
                    st.code(tool_info["output_type"], language="text")
                    st.markdown("**🧪 Validation schéma**")
                    if success:
                        st.success("✅ Schéma valide — Input/Output correct")
                    else:
                        st.error("❌ Validation échouée ou erreur détectée")

                if action == "http_get":
                    st.markdown("**🌐 Statut API**")
                    failure = st.session_state.inject_failure
                    if failure == "timeout":
                        st.error("⏱️ TIMEOUT — L'API ne répond pas")
                    elif failure == "429":
                        st.error(" X HTTP 429 — Too Many Requests (rate limit)")
                    elif failure == "invalid_json":
                        st.error(" JSON invalide reçu — parsing impossible")
                    elif success:
                        st.success(" -> HTTP 200 — Réponse valide")
                    else:
                        st.warning(" -> API indisponible — Fallback Mock utilisé")

                if retry > 0:
                    st.warning(f"🔁 Backtracking activé : {retry} tentative(s) supplémentaire(s)")
                if decision == "fallback":
                    st.info("🔄 Fallback : chemin alternatif utilisé (backup)")
    else:
        st.info(" Aucun tool call !!! — lancez un scénario.")


# ==============================
# TAB 3 — Rapport & KPIs
# ==============================
with tab3:
    st.subheader("📊 Rapport final & Indicateurs clés")

    if st.session_state.report:
        report = st.session_state.report

        with st.expander("🔍 JSON brut complet", expanded=False):
            st.json(report)

        st.divider()
        st.subheader("📈 KPIs")

        top_factories = report.get("top_factories", [])
        avg_defect    = report.get("avg_defect_rate", 0)
        delayed       = report.get("delayed_factories", [])
        alerts        = report.get("alerts", [])

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🏆 Usines Top",        ", ".join(top_factories) if top_factories else "—")
        k2.metric(" Taux défaut moyen !",  f"{avg_defect * 100:.1f}%")
        k3.metric("🕐 Usines en retard ",   ", ".join(delayed) if delayed else "Aucune")
        k4.metric(" Alertes !!!",            len(alerts))

        st.divider()

        if alerts:
            st.subheader("!!! Alertes")
            for alert in alerts:
                st.warning(f"• {alert}")
        else:
            st.success("✅ Aucune alerte — système nominal")

        if "industrial_trend" in report:
            st.divider()
            st.subheader("🌍 Indice industriel Tunisie (données API)")
            trend = report.get("industrial_trend", [])
            if trend:
                import pandas as pd
                df_trend = pd.DataFrame({
                    "Période": [f"T-{len(trend)-i}" for i in range(len(trend))],
                    "Indice":  trend
                })
                st.line_chart(df_trend.set_index("Période"))
    else:
        st.info("ℹ️ Aucun rapport — lancez un scénario.")


# ==============================
# TAB 4 — Cache DP & Métriques
# ==============================
with tab4:
    st.subheader("⚡ DP Memoization — Statistiques du Cache")

    if st.session_state.cache_stats:
        stats = st.session_state.cache_stats

        st.subheader("🔢 Cache — `compute_metrics`")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total appels",  stats['compute']['total_calls'])
        c2.metric("✅ Hits",        stats['compute']['hits'])
        c3.metric("❌ Misses",      stats['compute']['misses'])
        c4.metric("📊 Hit Ratio",   f"{stats['compute']['hit_ratio']}%")

        st.divider()

        st.subheader("🧠 Cache — Planner (décisions DP)")
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Total appels",  stats['planner']['total_calls'])
        p2.metric("✅ Hits",        stats['planner']['hits'])
        p3.metric("❌ Misses",      stats['planner']['misses'])
        p4.metric("📊 Hit Ratio",   f"{stats['planner']['hit_ratio']}%")

        st.divider()

        st.subheader("📊 BT seul vs BT + DP")
        import pandas as pd
        df_cmp = pd.DataFrame({
            "Critère": [
                "Recalcul des KPIs",
                "Recalcul décisions Planner",
                "Cache hit ratio",
                "Vitesse sur runs répétés",
                "Mémoire utilisée"
            ],
            "🔴 BT seul (sans DP)": [
                "❌ À chaque run",
                "❌ À chaque étape",
                "0%",
                "🐢 Lent",
                "✅ Faible"
            ],
            "🟢 BT + DP (avec cache)": [
                "✅ Réutilisé si même fichier",
                "✅ Mémorisé par (step, contexte)",
                f"{stats['compute']['hit_ratio']}%",
                " Plus rapide",
                "!! Légèrement plus élevée"
            ]
        })
        st.dataframe(df_cmp, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ Aucune statistique — lancez un scénario.")


# ==============================
# TAB 5 — Historique & Logs
# ==============================
with tab5:
    st.subheader("🕐 Historique des Runs (session courante)")

    if st.session_state.run_history:
        import pandas as pd
        df_hist = pd.DataFrame(st.session_state.run_history)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)

        if st.button("🗑️ Vider l'historique"):
            st.session_state.run_history = []
            st.rerun()
    else:
        st.info(" !! Aucun run dans cette session.")

    st.divider()

    st.subheader("📁 Logs sauvegardés (fichiers JSON)")
    st.caption("Sauvegardés automatiquement dans `logs/` après chaque run.")

    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')

    if os.path.exists(logs_dir):
        log_files = sorted(glob.glob(os.path.join(logs_dir, "*.json")), reverse=True)

        if log_files:
            st.success(f"✅ {len(log_files)} fichier(s) de log trouvé(s)")
            log_names = [os.path.basename(f) for f in log_files]
            selected_log = st.selectbox("Choisir un log :", options=log_names, index=0)
            selected_path = os.path.join(logs_dir, selected_log)

            try:
                with open(selected_path, "r", encoding="utf-8") as f:
                    log_data = json.load(f)

                log_str          = json.dumps(log_data, indent=2, ensure_ascii=False)
                log_str_redacted = redact_sensitive(log_str)
                log_data_red     = json.loads(log_str_redacted)

                li1, li2, li3 = st.columns(3)
                li1.metric("Run ID",          log_data_red.get("run_id", "—"))
                li2.metric("Étapes",          len(log_data_red.get("journal", [])))
                li3.metric("Erreur injectée", log_data_red.get("error_injected") or "Aucune")

                with st.expander("📄 Contenu complet du log (redacté)", expanded=False):
                    st.json(log_data_red)

                journal_log = log_data_red.get("journal", [])
                if journal_log:
                    st.markdown("**📋 Étapes du run :**")
                    for step in journal_log:
                        icon = "✅" if step.get("success") else "❌"
                        st.write(
                            f"{icon} `{step.get('step_id')}` — "
                            f"**{step.get('action')}** → *{step.get('decision')}*"
                        )

                cache_log = log_data_red.get("cache_stats")
                if cache_log:
                    st.markdown("**⚡ Cache DP au moment du run :**")
                    st.write(
                        f"Compute hit ratio : **{cache_log['compute']['hit_ratio']}%** | "
                        f"Planner hit ratio : **{cache_log['planner']['hit_ratio']}%**"
                    )

            except Exception as e:
                st.error(f"Erreur lecture log : {redact_sensitive(str(e))}")
        else:
            st.warning("⚠️ Aucun fichier de log. Lancez un scénario pour en générer.")
    else:
        st.warning("⚠️ Dossier `logs/` introuvable — sera créé au premier run.")

    st.divider()

    st.subheader("🛡️ Safety & Policy Panel")
    st.caption("Règles de sécurité appliquées par le système à chaque run.")

    safety_rules = {
        "🔒 Redaction données sensibles":  "✅ Activée — chemins, tokens, IPs masqués avant affichage",
        "📋 Allow-list outils":            "✅ read_csv, validate_schema, compute_metrics, http_get, generate_report uniquement",
        "⏱️ MAX_STEPS":                    "✅ Maximum 10 étapes par run",
        "🔁 MAX_RETRY":                    "✅ Maximum 3 tentatives par action avant fallback",
        "✂️ Pruning":                      "✅ Arrêt immédiat si schéma invalide ou erreur fatale",
        "🔙 Backtracking":                 "✅ Fichier principal manquant → backup automatique",
        "🌐 API Allow-list":               "✅ Seuls endpoints Tunisia World Bank / Mock autorisés",
        "🔀 Concurrence":                  "✅ Chaque run a son propre journal isolé (no state leakage)"
    }

    for rule, status in safety_rules.items():
        st.write(f"**{rule}** : {status}")
    #C’est l’interface graphique principale (Streamlit). Elle permet de : lancer le Scénario 1 avec un bouton,
#voir le journal d’exécution (Plan → Execute → Critic),afficher le rapport JSON final
#visualiser les KPIs sous forme de métriques
#voir les alertes détectées