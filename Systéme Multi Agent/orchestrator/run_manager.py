import uuid
from datetime import datetime

class RunManager:
    def __init__(self, run_id=None):
        self.run_id = run_id or str(uuid.uuid4())[:8]
        self.steps = []
        self.status = "running"
        self.start_time = datetime.now()

    def log_step(self, phase, action, result, error=None, step_id=None):
        step = {
            "step_id": step_id or len(self.steps) + 1,
            "phase": phase,  # Plan, Execute, Critic
            "action": action,
            "result": result,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.steps.append(step)

    def finish(self, success):
        self.status = "success" if success else "failed"
        self.end_time = datetime.now()

    def summary(self):
        return {
            "run_id": self.run_id,
            "status": self.status,
            "duration_sec": (self.end_time - self.start_time).total_seconds() if hasattr(self, 'end_time') else None,
            "steps": self.steps
        }

    def print_summary(self):
        print("\n" + "="*60)
        print(f"RÉSUMÉ DU RUN : {self.run_id}")
        print(f"   Statut : {self.status}")
        print(f"   Étapes : {len(self.steps)}")
        print("="*60)
        for step in self.steps:
            status_icon = "✓" if not step.get("error") else "❌"
            print(f"   {status_icon} Étape {step['step_id']} | {step['phase']} | {step['action']}")
            if step.get("error"):
                print(f"        !!! Erreur : {step['error']}")
        print("="*60)
        #Ce fichier gère le suivi de chaque exécution (run).
        #  Il crée un identifiant unique (run_id),
        #  enregistre chaque étape (Plan → Execute → Critic),*
        #  stocke les erreurs et le temps d’exécution.
        #  Il permet aussi d’afficher un résumé clair à la fin.