import json
import random
import math
import time
from pathlib import Path

# === PARAMETERS ===

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

# Antennas
ANT_TOP = 0.0
ANT_BOTTOM = math.pi
ANT_CENTER = math.pi / 2
_ant_noise = [0.0, 0.0]

# Other
MIN_DURATION = 0.4   # Rapid movement
MAX_DURATION = 3.0   # Slow movement
# ==================

RULES_FILE = Path(__file__).parent / "rules" / "rules_2.json"


with RULES_FILE.open("r", encoding="utf-8") as f:
    RULES = json.load(f)


def noise(sigma, k=0.1):
    return random.uniform(-k * sigma, k * sigma)


def rint(a, b):
    return random.randint(a, b)


def wrap_angle(theta):
    """Keep angle in [0, 2pi]."""
    return theta % (2 * math.pi)


def moving_antennas(P, A, D, t=None):
    """
    P, A, D ∈ [0,1]
    Returns: [ant0, ant1] in radians, 0=up, pi=down
    """
        
    global _ant_noise

    if t is None:
        t = time.time()

    # --- Base direction ---
    # Higher pleasure => antennas go up
    base_angle = ANT_BOTTOM - 1.1 * P * (ANT_BOTTOM - ANT_TOP)
    print("\nbase = ", base_angle)

    # --- Non-symmetry condition ---
    # Weak dominance and a bit of arousal means confusion => non-symmetry
    non_symmetric = D < 0.6 and A > 0.3

    # --- Base movement ---
    ant0 = base_angle + 0.2 * random.uniform(-A * math.pi, A * math.pi) 
    print("base + osc = ", ant0)
    print(" ")
    ant1 = ant0 if non_symmetric else - (ant0 - ANT_TOP)

    # --- Slow random drift (arousal and dominance-dependent) ---
    drift_step = 0.1 * A * (1/D)
    drift_limit = 2 * drift_step

    for i in (0, 1):
        _ant_noise[i] += random.uniform(-drift_step, drift_step)
        _ant_noise[i] = max(-drift_limit, min(drift_limit, _ant_noise[i]))

    ant0 += _ant_noise[0]
    ant1 += _ant_noise[1]

    return [
        round(wrap_angle(ant0), 2),
        round(wrap_angle(ant1), 2),
    ]


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


def generate_pose(P, A, D):
    """Convert PAD coordinates (from 0 to 1) into a robot pose."""

    # --- PAD center (neutral) ---
    x_c = 0
    y_c = 0
    z_c = 0 

    # --- Position (x, y, z) according to Arousal and Dominance ---
    x = rint(int(x_c - abs(MIN_X)*(A)), int(x_c + MAX_X*A)) # The more arousal, the wider movements
    y = rint(int(y_c - MAX_Y*A), int(y_c + MAX_Y*A))
    z = D * rint(int(z_c - MAX_Z*(1 - D)), int(z_c + MAX_Z*D)) # The more dominance, the higher the head

    # --- Apply existing rules for head orientation ---
    roll_r  = RULES["roll_from_y"]
    pitch_r = RULES["pitch_from_z"]
    yaw_r   = RULES["yaw_from_x"]

    roll  = roll_r["a"]  * y + roll_r["b"]  + noise(roll_r["sigma"], 0.5)
    pitch = pitch_r["a"] * z + pitch_r["b"] + noise(pitch_r["sigma"], 0.5)
    yaw   = yaw_r["a"]   * x + yaw_r["b"]   + noise(yaw_r["sigma"], 0.5)

    # --- Orientation amplified with Aroussal ---
    roll *= A
    yaw  *= A

    # If pleasure is weak, the pitch goes high; if pleasure is high, pitch goes lower
    pitch -= 1.5 * (2 * P - 1) * abs(rint(MIN_PITCH, -MIN_PITCH))
    pitch *= A # Someone crazy makes wide movements, while a weak arousal makes narrow ones

    # --- Body yaw (softer movement, influenced by Arousal) ---
    body_center = 0
    body_amp = 0.2 * A * yaw # Here = factor changed
    body_yaw = rint(int(body_center - abs(body_amp)), int(body_center + abs(body_amp)))

    # --- Dominance influence ---
    body_yaw *= 1/D # confident robot looks more forward
    yaw *= 1/D
    
    # --- Duration (longer for low Arousal, shorter for high Arousal) ---
    duration = MIN_DURATION + (1 - A) * (MAX_DURATION - MIN_DURATION)
    jitter = 1 + random.uniform(-0.5, 0.5) * A
    duration *= jitter

    # --- Safety clamps ---
    pitch = int(max(-abs(MIN_PITCH), min(MAX_PITCH, pitch)))
    roll = int(max(-MAX_ROLL, min(MAX_ROLL, roll)))
    yaw = int(max(-MAX_YAW, min(MAX_YAW, yaw)))
    body_yaw = max(-MAX_BODY_YAW, min(MAX_BODY_YAW, body_yaw))
    duration = max(MIN_DURATION, min(MAX_DURATION, duration))

    # --- Method ---
    method = "minjerk"

    # --- Answer ---
    return {
        "x": x,
        "y": y,
        "z": z,
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw,
        "antennas": moving_antennas(P, A, D),
        "duration": round(duration, 2),
        "method": method,
        "body_yaw": round(body_yaw, 2),
    }
