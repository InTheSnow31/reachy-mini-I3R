import json
import random
import math
import time
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

# Antennas
ANT_TOP = 0.0
ANT_BOTTOM = math.pi
ANT_CENTER = math.pi / 2

# Other
MIN_DURATION = 0.4   # Rapid movement
MAX_DURATION = 3.0   # Slow movement
# ==================

# random.seed(SEED)

RULES_FILE = Path(__file__).parent / "rules" / "rules_2.json"


with RULES_FILE.open("r", encoding="utf-8") as f:
    RULES = json.load(f)


def noise(sigma, k=0.1):
    return random.uniform(-k * sigma, k * sigma)


def rint(a, b):
    return random.randint(a, b)


def wrap_angle(theta):
    """Keep angle in [0, 2pi)."""
    return theta % (2 * math.pi)


def antennas_from_direction(direction, sense=1, spread=0.3):
    """
    direction [-1, 1] : down → up
    sense = +1 (symmetrical) or -1 (opposite)
    spread [0, pi/2]
    """

    # map direction to angle
    # -1 → pi (down)
    #  0 → pi/2 (neutral)
    # +1 → 0 (up)
    base_angle = (1 - direction) * (math.pi / 2)

    delta = spread * direction

    ant0 = wrap_angle(base_angle + delta)
    ant1 = wrap_angle(base_angle + sense * delta)

    return [round(ant0, 2), round(ant1, 2)]

def moving_antennas(P, A, D, t=None):
    """
    P, A, D ∈ [0, 1]
    t : time in seconds (if None → time.time())
    """

    if t is None:
        t = time.time()

    # --- Base direction (Pleasure) ---
    # 0 → down, 1 → up
    base_angle = (1 - P) * (math.pi / 2)

    # --- Arousal controls motion ---
    amp = A * (math.pi / 6)        # movement amplitude
    freq = 0.2 + 1.5 * A           # speed of oscillation

    phase = 2 * math.pi * freq * t

    # --- Dominance controls symmetry ---
    symmetric = D > 0.5

    osc = amp * math.sin(phase)

    ant0 = base_angle + osc
    
    if symmetric:
        ant1 = -ant0
    else:
        ant1 = ant0

    # --- Small noise (life) ---
    jitter = 0.05 * A
    ant0 += random.uniform(-jitter, jitter)
    ant1 += random.uniform(-jitter, jitter)

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


def generate_pose_from_pad(P, A, D):
    """Convert PAD coordinates (from 0 to 1) into a robot pose."""

    # --- PAD center (neutral) ---
    x_c = 0
    y_c = 0
    z_c = 0 

    # --- Position (x, y, z) according to Arousal and Pleasure ---
    x = rint(int(x_c - abs(MIN_X)*(A)), int(x_c + MAX_X*A)) # The more arousal, the wider movements
    y = rint(int(y_c - MAX_Y*(A)), int(y_c + MAX_Y*A))
    z = P * rint(int(z_c - MAX_Z*(1 - P)), int(z_c + MAX_Z*P)) # The more pleasure, the higher the head

    # --- Apply existing rules for head orientation ---
    roll_r  = RULES["roll_from_y"]
    pitch_r = RULES["pitch_from_z"]
    yaw_r   = RULES["yaw_from_x"]

    roll  = roll_r["a"]  * y + roll_r["b"]  + noise(roll_r["sigma"], 0.5)
    pitch = pitch_r["a"] * z + pitch_r["b"] + noise(pitch_r["sigma"], 0.5)
    yaw   = yaw_r["a"]   * x + yaw_r["b"]   + noise(yaw_r["sigma"], 0.5)

    # --- Orientation according to Dominance ---
    roll *= A
    yaw  *= A

    # If dominance is weak, the pitch goes high; if dominance is high, pitch goes lower
    pitch += (2 * D - 1) * rint(MIN_PITCH, MAX_PITCH)
    pitch *= A # Someone crazy makes wide movements, while a weak arousal makes narrow ones

    # --- Body yaw (softer movement, influenced by Arousal) ---
    body_center = 0
    body_amp = 0.05 * A * yaw
    body_yaw = rint(int(body_center - body_amp), int(body_center + body_amp))

    # --- Antennas according to Arousal and Dominance ---
    # ant0 = random.uniform(0, (1-D) * (1-A) * MAX_ANTENNAS)
    # ant1 = random.uniform(0, (1-D) * (1-A) * MAX_ANTENNAS)
    direction = 2 * P - 1        # [0,1] → [-1,1]
    spread = A * (math.pi / 4)
    sense = 1 if D > 0.5 else -1

    antennas = antennas_from_direction(direction, sense, spread)

    # --- Dominance influence ---
    body_yaw *= 1/D # confident robot looks more forward
    yaw *= 1/D

    # --- Safety clamps ---
    pitch = int(max(-abs(MIN_PITCH), min(MAX_PITCH, pitch)))
    roll = int(max(-MAX_ROLL, min(MAX_ROLL, roll)))
    yaw = int(max(-MAX_YAW, min(MAX_YAW, yaw)))
    body_yaw = max(-MAX_BODY_YAW, min(MAX_BODY_YAW, body_yaw))

    # --- Duration (longer for low Arousal, shorter for high Arousal) ---
    duration = MIN_DURATION + (1 - A) * (MAX_DURATION - MIN_DURATION)

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
