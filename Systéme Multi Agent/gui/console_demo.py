import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'orchestrator'))

from agent_loop import run_agent_loop

def demo_console():
    print("\n" + "="*60)
    print(" DÉMO CONSOLE - Système Multi-Agent Tunisie")
    print("="*60)

    # CORRECTION : run_agent_loop retourne 3 valeurs
    report, journal, cache_stats = run_agent_loop(run_id="demo_console", use_scenario2=False)

    print("\n RAPPORT FINAL :")
    if report:
        for key, value in report.items():
            print(f"   {key}: {value}")
    else:
        print("   Aucun rapport généré")

    print(f"\n CACHE DP :")
    print(f"   Compute hit ratio : {cache_stats['compute']['hit_ratio']}%")
    print(f"   Planner hit ratio : {cache_stats['planner']['hit_ratio']}%")

if __name__ == "__main__":
    demo_console()
    #Une version simple dans le terminal (console) pour tester le système sans interface graphique.
    #ynajjem ylaunchi scénario 1,ywarri journal (kol step chnowa sar), ywarri rapport final,ken fama erreur  yaffichiha
    #pour l'exécuter:dans le terminal on ecrit * python gui/console_demo.py *
    #  Elle lance le Scénario 1 et affiche le rapport final dans la console.