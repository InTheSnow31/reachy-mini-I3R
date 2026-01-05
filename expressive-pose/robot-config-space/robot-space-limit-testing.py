import json
import random
from pathlib import Path

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

# ========= PARAMÈTRES =========
N_SAMPLES = 1000          # nombre de tests à faire
DURATION = 1.5            # durée de chaque mouvement
OUTPUT_FILE = "pose_dataset_3.json"
SEED = 42                 # pour reproductibilité
# ==============================

random.seed(SEED)

def rint(a, b):
    """Entier uniforme inclusif."""
    return random.randint(a, b)


def rfloat_1(a, b):
    """Flottant à 1 décimale."""
    return round(random.uniform(a, b), 1)


def sample_pose():
    """Échantillonnage volontairement large (agressif)."""
    return {
        "x": rint(-40, 40),
        "y": rint(-60, 60),
        "z": rint(-60, 60),
        "roll": rint(-50, 50),
        "pitch": rint(-50, 50),
        "yaw": rint(-65, 65),
        "body_yaw": rint(-20, 20),
        "antennas": [
            rfloat_1(0.0, 3.16),
            rfloat_1(0.0, 3.16),
        ],
    }


def ask_user():
    """Demande un label proprement."""
    while True:
        v = input("Pose atteignable ? (1 = OK / 0 = NOK / q = quitter) : ").strip()
        if v in ("0", "1"):
            return int(v)
        if v.lower() == "q":
            return None


def main():
    dataset = []

    print(f"Début de la collecte ({N_SAMPLES} poses max)")
    print("Regarde la simu, puis tape 1 / 0")
    print("-" * 50)

    with ReachyMini() as reachy:
        for i in range(N_SAMPLES):
            pose = sample_pose()

            print(f"\nTest {i+1}/{N_SAMPLES}")
            print(pose)

            head = create_head_pose(
                x=pose["x"],
                y=pose["y"],
                z=pose["z"],
                roll=pose["roll"],
                pitch=pose["pitch"],
                yaw=pose["yaw"],
                mm=True,
                degrees=True,
            )

            try:
                reachy.goto_target(
                    head=head,
                    body_yaw=pose["body_yaw"],
                    antennas=pose["antennas"],
                    duration=DURATION,
                )
            except Exception as e:
                print("Exception pendant l'exécution :", e)
                label = 0
            else:
                label = ask_user()
                if label is None:
                    break

            dataset.append(
                {
                    "pose": pose,
                    "label": label,
                    "id": i,
                }
            )

        print("\nCollecte terminée.")

    # Sauvegarde
    out = Path(OUTPUT_FILE)
    with out.open("w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    print(f"Dataset sauvegardé dans : {out.resolve()}")
    print(f"Nombre d'échantillons : {len(dataset)}")


if __name__ == "__main__":
    main()
