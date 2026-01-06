import json
import random

# === PARAMETERS ===
SEED = 42
# ==================

random.seed(SEED)

with open("rules/rules_2.json") as f:
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
