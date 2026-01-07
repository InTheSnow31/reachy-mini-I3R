import json
import random
from pathlib import Path

# === PARAMETERS ===
# SEED = 42

# Prismatic values (mm)
MIN_X = -20
MAX_X = 32
MAX_Y = 60
MAX_Z = 60

# Rotoid values (degree)
MAX_ROLL = 50
MIN_PITCH = -42
MAX_PITCH = 35
MAX_YAW = 90
MAX_BODY_YAW = 10

# Other
MIN_DURATION = 0.4   # Rapid movement
MAX_DURATION = 3.0   # Slow movement
MAX_ANTENNAS = 3.14
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
    """Convert PAD coordinates (from 0 to 1) into a robot pose."""

    # --- PAD center (neutral) ---
    x_c = 0
    y_c = 0
    z_c = 0 

    # --- Position (x, y, z) according to Arousal and Pleasure ---
    x = rint(int(x_c - abs(MIN_X)*A), int(x_c + MAX_X*A))
    y = rint(int(y_c - MAX_Y*A), int(y_c + MAX_Y*A))
    z = rint(int(z_c - MAX_Z*P), int(z_c + MAX_Z*P))

    # --- Apply existing rules for head orientation ---
    roll_r  = RULES["roll_from_y"]
    pitch_r = RULES["pitch_from_z"]
    yaw_r   = RULES["yaw_from_x"]

    roll  = roll_r["a"]  * y + roll_r["b"]  + noise(roll_r["sigma"], 0.05)
    pitch = pitch_r["a"] * z + pitch_r["b"] + noise(pitch_r["sigma"], 0.05)
    yaw   = yaw_r["a"]   * x + yaw_r["b"]   + noise(yaw_r["sigma"], 0.05)

    # --- Orientation according to Dominance ---
    roll += int(D * 20)
    yaw  += int(D * 30)

    # --- Body yaw (softer movement, influenced by Arousal) ---
    body_center = 0.2 * yaw
    body_amp = 0.5 * MAX_BODY_YAW * A
    body_yaw = rint(int(body_center - body_amp), int(body_center + body_amp))

    # --- Antennas according to Arousal and Dominance ---
    ant0 = random.uniform(0, (1-D) * (1-A) * MAX_ANTENNAS)
    ant1 = random.uniform(0, (1-D) * (1-A) * MAX_ANTENNAS)

    # --- Dominance influence ---
    body_yaw *= 1/D # confident robot looks more forward
    yaw *= 1/D

    if D > 0.5:  
        ant1 = -ant0 # symetrical antennas

    # --- Safety clamps ---
    pitch = int(max(-abs(MIN_PITCH), min(MIN_PITCH, pitch)))
    roll = int(max(-MAX_ROLL, min(MAX_ROLL, roll)))
    yaw = int(max(-MAX_YAW, min(MAX_YAW, yaw)))
    body_yaw = max(-MAX_BODY_YAW, min(MAX_BODY_YAW, body_yaw))

    # --- Duration (longer for low Arousal, shorter for high Arousal) ---
    duration = MIN_DURATION + (1 - A) * (MAX_DURATION - MIN_DURATION)

    method = "minjerk"

    return {
        "x": x,
        "y": y,
        "z": z,
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw,
        "antennas": [round(ant0, 2), round(ant1, 2)],
        "duration": round(duration, 2),
        "method": method,
        "body_yaw": round(body_yaw, 2),
    }
