import json
import random
from pathlib import Path

# === PARAMETERS ===
# SEED = 42
D_MIN = 0.4   # Rapid movement
D_MAX = 3.0   # Slow movement
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

    A_mag = abs(A)

    # PAD center
    x_c = 0
    y_c = 0
    z_c = int(P * 60)

    # Amplitude according to Arousal
    x = rint(int(x_c - 40*A_mag), int(x_c + 40*A_mag))
    y = rint(int(y_c - 60*A_mag), int(y_c + 60*A_mag))
    z = rint(int(z_c - 10), int(z_c + 10))

    # Apply existing rules to stay physically real
    pitch_r = RULES["pitch_from_z"]
    roll_r  = RULES["roll_from_y"]
    yaw_r   = RULES["yaw_from_x"]

    pitch = pitch_r["a"] * z + pitch_r["b"] + noise(pitch_r["sigma"], 0.05)
    roll  = roll_r["a"]  * y + roll_r["b"]  + noise(roll_r["sigma"], 0.05)
    yaw   = yaw_r["a"]   * x + yaw_r["b"]   + noise(yaw_r["sigma"], 0.05)

    # roll and yaw according to Dominance
    roll += D * 20
    yaw  += D * 30

    # Antennas according to Arousal and Dominance
    ant0 = abs(A + D) * 1.5 + random.uniform(-0.2, 0.2)
    ant1 = abs(A - D) * 1.5 + random.uniform(-0.2, 0.2)

    # Safety clamps
    pitch = int(max(-30, min(30, pitch)))
    roll  = int(max(-30, min(30, roll)))
    yaw   = int(max(-45, min(45, yaw)))
    ant0  = max(0, min(3.16, ant0))
    ant1  = max(0, min(3.16, ant1))

    # Duration
    duration = D_MAX - A_mag * (D_MAX - D_MIN)

    # Method
    method = "minjerk"

    return {
        "x": x,
        "y": y,
        "z": z,
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw,
        "antennas": [round(ant0, 2), round(ant1, 2)],
        "duration": duration,
        "method": method,
        "body_yaw": 0
    }