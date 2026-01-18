import json
import random
from pathlib import Path

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

# ========= PARAMÈTRES =========
N_SAMPLES = 10         # nombre de tests à faire
DURATION = 1.5            # durée de chaque mouvement
OUTPUT_FILE = "pose_datasets/pose_dataset_4.json"
SEED = 42                 # pour reproductibilité
# ==============================

random.seed(SEED)

# Chargement des regles
with open("rules/rules_2.json") as f:
    RULES = json.load(f)
# Bruit pour l'ecart-type
def noise(sigma, k=0.5):
    """Bruit borné (± k * sigma)."""
    return random.uniform(-k * sigma, k * sigma)

def rint(a, b):
    """Entier uniforme inclusif."""
    return random.randint(a, b)


def rfloat_1(a, b):
    """Flottant à 1 décimale."""
    return round(random.uniform(a, b), 1)


def sample_pose():
    # --- variables libres ---
    x = rint(-40, 40)
    y = rint(-60, 60)
    z = rint(-60, 60)

    # --- règles ---
    pitch_rule = RULES["pitch_from_z"]
    roll_rule = RULES["roll_from_y"]
    yaw_rule = RULES["yaw_from_x"]

    pitch = (
        pitch_rule["a"] * z
        + pitch_rule["b"]
        + noise(pitch_rule["sigma"], k=0.01)
    )

    roll = (
        roll_rule["a"] * y
        + roll_rule["b"]
        + noise(roll_rule["sigma"], k=0.01)
    )

    yaw = (
        yaw_rule["a"] * x
        + yaw_rule["b"]
        + noise(yaw_rule["sigma"], k=0.01)
    )

    # --- hard safety clamps ---
    pitch = int(max(-30, min(30, pitch)))
    roll = int(max(-30, min(30, roll)))
    yaw = int(max(-45, min(45, yaw)))

    return {
        "x": x,
        "y": y,
        "z": z,
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw,
        "body_yaw": 0,
        "antennas": [0, 0],
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
