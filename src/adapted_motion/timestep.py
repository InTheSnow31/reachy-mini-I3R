import numpy as np
from normalisation_PAD.norm import positive_norm

def timestep(arousal: float) -> float:
    """
    - Arousal near 0 → slower movement
    - Arousal far from 0 → faster movement
    This partially affects the fluidity of the motion.
    """
    arousal_norm = positive_norm("Arousal", arousal)

    dt_min = 0.01   # fast but safe
    dt_max = 0.05   # slow, deliberate

    # Compute timestep: decreases as arousal increases
    dt = dt_max - arousal_norm * (dt_max - dt_min)

    return np.clip(dt, dt_min, dt_max)