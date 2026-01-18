import numpy as np

def amp_max(
    arousal: float,
    z_norm: float,         # normalized between 0 (min pitch) and 1 (max pitch)
    dominance: float = 0.0, # dominance value, affects minimum amplitude
    A_max_neutral: float = np.pi/3,  # 60° in radians
    A_min_default: float = 0.175     # 10° in radians
) -> float:
    """
    Compute the maximum movement amplitude (radians) based on:
    - z_norm: normalized center pitch (0=min, 1=max)
    - arousal: motion energy/intensity
    - dominance: affects minimum amplitude

    Rules:
    - Non-linear amplification: extreme z_norm → lower amplitude
    - Minimum amplitude depends on dominance:
        - positive dominance → A_min = 30° (~0.52 rad)
        - negative or zero dominance → A_min = default (~10°)
    - Maximum amplitude scales with arousal
    """
    # Determine minimum amplitude based on dominance
    A_min = 0.52 if dominance > 0 else A_min_default  # 30° if dominant, else default 10°

    # Non-linear amplification based on z_norm (inverse extremes)
    amplification = (1.0 - z_norm) ** 2
    amplification = np.clip(amplification, 0.0, 1.0)

    # Combine min, max, amplification, and arousal
    A_max = A_min + (A_max_neutral - A_min) * amplification * (0.5 + 0.5 * arousal)

    return A_max