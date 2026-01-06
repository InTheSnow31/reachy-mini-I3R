import json
import random
from pathlib import Path

# === PARAMETERS ===
# SEED = 42
# ==================

# random.seed(SEED)

RULES_FILE = Path(__file__).parent / "rules" / "rules_2.json"

with RULES_FILE.open("r", encoding="utf-8") as f:
    RULES = json.load(f)

def noise(sigma, k=0.1):
    return random.uniform(-k * sigma, k * sigma)

def rint(a, b):
    return random.randint(a, b)

def sample_pose():
    x = rint(-40, 40)
    y = rint(-60, 60)
    z = rint(-60, 60)

    pitch_r = RULES["pitch_from_z"]
    roll_r  = RULES["roll_from_y"]
    yaw_r   = RULES["yaw_from_x"]

    pitch = pitch_r["a"] * z + pitch_r["b"] + noise(pitch_r["sigma"], 0.01)
    roll  = roll_r["a"]  * y + roll_r["b"]  + noise(roll_r["sigma"], 0.01)
    yaw   = yaw_r["a"]   * x + yaw_r["b"]   + noise(yaw_r["sigma"], 0.01)

    return {
        "x": x,
        "y": y,
        "z": z,
        "roll": int(max(-30, min(30, roll))),
        "pitch": int(max(-30, min(30, pitch))),
        "yaw": int(max(-45, min(45, yaw))),
        "body_yaw": 0,
        "antennas": [0, 0],
    }


def generate_pose_from_pad(P, A, D):
    """Convert PAD coordinates into a robot pose."""
    # variables libres (amplitude selon Arousal)
    x = int(A * 40)   # ±40 mm max
    y = int(A * 60)
    z = int(P * 60)

    # appliquer règles existantes
    pitch_r = RULES["pitch_from_z"]
    roll_r  = RULES["roll_from_y"]
    yaw_r   = RULES["yaw_from_x"]

    pitch = pitch_r["a"] * z + pitch_r["b"]
    roll  = roll_r["a"]  * y + roll_r["b"]
    yaw   = yaw_r["a"]   * x + yaw_r["b"]

    # roll et yaw selon Dominance
    roll += int(D * 20)
    yaw  += int(D * 30)

    # antennes selon Arousal et Dominance
    ant0 = round(abs(A + D) * 1.5, 1)
    ant1 = round(abs(A - D) * 1.5, 1)

    # clamps de sécurité
    pitch = max(-30, min(30, pitch))
    roll  = max(-30, min(30, roll))
    yaw   = max(-45, min(45, yaw))
    ant0 = max(0, min(3.16, ant0))
    ant1 = max(0, min(3.16, ant1))

    return {
        "x": x,
        "y": y,
        "z": z,
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw,
        "body_yaw": 0,
        "antennas": [ant0, ant1],
    }