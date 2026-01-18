from typing import Dict, Any, List, Optional

import json
import random
import math
import time
from pathlib import Path


# === CONSTANT PARAMETERS ===

# Prismatic limits (millimeters)
MIN_X: int = -20
MAX_X: int = 32
MAX_Y: int = 60
MAX_Z: int = 60

# Rotational limits (degrees)
MAX_ROLL: int = 50
MIN_PITCH: int = -42
MAX_PITCH: int = 35
MAX_YAW: int = 90
MAX_BODY_YAW: int = 10

# Antenna reference angles (radians)
ANT_TOP: float = 0.0
ANT_BOTTOM: float = math.pi
ANT_CENTER: float = math.pi / 2

# Internal antenna noise state (slow drift)
_ant_noise: List[float] = [0.0, 0.0]

# Timing
MIN_DURATION: float = 0.4   # Fast movement
MAX_DURATION: float = 3.0   # Slow movement

# ===========================

RULES_FILE: Path = Path(__file__).parent / "rules" / "rules_2.json"

with RULES_FILE.open("r", encoding="utf-8") as f:
    RULES: Dict[str, Any] = json.load(f)


def noise(sigma: float, k: float = 0.1) -> float:
    """
    Generate bounded uniform noise proportional to a sigma value.
    """
    return random.uniform(-k * sigma, k * sigma)


def rint(a: int, b: int) -> int:
    """
    Return a random integer between a and b (inclusive).
    """
    return random.randint(a, b)


def wrap_angle(theta: float) -> float:
    """
    Wrap an angle into the [0, 2pi] range.
    """
    return theta % (2 * math.pi)


def moving_antennas(
    P: float,
    A: float,
    D: float,
    t: Optional[float] = None,
) -> List[float]:
    """
    Compute antenna angles based on PAD values.

    Returns two angles in radians:
    - 0 rad = up
    - pi rad = down
    """

    global _ant_noise

    if t is None:
        t = time.time()

    # --- Base direction ---
    # Higher pleasure lifts the antennas upward
    base_angle: float = ANT_BOTTOM - 1.1 * P * (ANT_BOTTOM - ANT_TOP)

    # --- Symmetry breaking ---
    # Low dominance + some arousal = confused / asymmetric antennas
    non_symmetric: bool = D < 0.6 and A > 0.3

    # --- Base oscillation ---
    ant0: float = base_angle + 0.2 * random.uniform(
        -A * math.pi,
        A * math.pi,
    )

    ant1: float = ant0 if non_symmetric else -(ant0 - ANT_TOP)

    # --- Slow random drift (memory effect) ---
    drift_step: float = 0.1 * A * (1 / D)
    drift_limit: float = 2 * drift_step

    for i in (0, 1):
        _ant_noise[i] += random.uniform(-drift_step, drift_step)
        _ant_noise[i] = max(
            -drift_limit,
            min(drift_limit, _ant_noise[i]),
        )

    ant0 += _ant_noise[0]
    ant1 += _ant_noise[1]

    return [
        round(wrap_angle(ant0), 2),
        round(wrap_angle(ant1), 2),
    ]


def sample_pose() -> Dict[str, Any]:
    """
    Sample a random valid robot pose using linear rules.
    """

    x: int = rint(-40, 40)
    y: int = rint(-60, 60)
    z: int = rint(-60, 60)

    pitch_r = RULES["pitch_from_z"]
    roll_r = RULES["roll_from_y"]
    yaw_r = RULES["yaw_from_x"]

    pitch: float = pitch_r["a"] * z + pitch_r["b"] + noise(pitch_r["sigma"], 0.01)
    roll: float = roll_r["a"] * y + roll_r["b"] + noise(roll_r["sigma"], 0.01)
    yaw: float = yaw_r["a"] * x + yaw_r["b"] + noise(yaw_r["sigma"], 0.01)

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


def generate_pose(P: float, A: float, D: float) -> Dict[str, Any]:
    """
    Convert PAD coordinates (values in [0, 1]) into a robot pose.

    The mapping mixes rule-based kinematics with stochastic modulation.
    """

    # --- Neutral center ---
    x_c: int = 0
    y_c: int = 0
    z_c: int = 0

    # --- Position ---
    # Arousal controls spatial amplitude
    x: int = rint(
        int(x_c - abs(MIN_X) * A),
        int(x_c + MAX_X * A),
    )
    y: int = rint(
        int(y_c - MAX_Y * A),
        int(y_c + MAX_Y * A),
    )

    # Dominance controls vertical posture
    z: float = D * rint(
        int(z_c - MAX_Z * (1 - D)),
        int(z_c + MAX_Z * D),
    )

    # --- Orientation from learned rules ---
    roll_r = RULES["roll_from_y"]
    pitch_r = RULES["pitch_from_z"]
    yaw_r = RULES["yaw_from_x"]

    roll: float = roll_r["a"] * y + roll_r["b"] + noise(roll_r["sigma"], 0.5)
    pitch: float = pitch_r["a"] * z + pitch_r["b"] + noise(pitch_r["sigma"], 0.5)
    yaw: float = yaw_r["a"] * x + yaw_r["b"] + noise(yaw_r["sigma"], 0.5)

    # --- Arousal amplification ---
    roll *= A
    yaw *= A

    # Pleasure biases pitch direction
    pitch -= 1.5 * (2 * P - 1) * abs(rint(MIN_PITCH, -MIN_PITCH))
    pitch *= A

    # --- Body yaw ---
    body_center: int = 0
    body_amp: float = 0.2 * A * yaw
    body_yaw: float = rint(
        int(body_center - abs(body_amp)),
        int(body_center + abs(body_amp)),
    )

    # --- Dominance stabilization ---
    body_yaw *= 1 / D
    yaw *= 1 / D

    # --- Duration ---
    duration: float = MIN_DURATION + (1 - A) * (MAX_DURATION - MIN_DURATION)
    jitter: float = 1 + random.uniform(-0.5, 0.5) * A
    duration *= jitter

    # --- Safety clamps ---
    pitch = int(max(-abs(MIN_PITCH), min(MAX_PITCH, pitch)))
    roll = int(max(-MAX_ROLL, min(MAX_ROLL, roll)))
    yaw = int(max(-MAX_YAW, min(MAX_YAW, yaw)))
    body_yaw = max(-MAX_BODY_YAW, min(MAX_BODY_YAW, body_yaw))
    duration = max(MIN_DURATION, min(MAX_DURATION, duration))

    return {
        "x": x,
        "y": y,
        "z": z,
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw,
        "antennas": moving_antennas(P, A, D),
        "duration": round(duration, 2),
        "method": "minjerk",
        "body_yaw": round(body_yaw, 2),
    }
