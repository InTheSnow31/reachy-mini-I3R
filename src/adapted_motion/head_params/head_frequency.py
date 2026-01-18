import numpy as np
from adapted_motion.normalisation_PAD.norm import positive_norm, signed_norm

def head_frequency(A_t: float, dominance: float, A_max: float = 0.3) -> float:
    """
    Compute the instantaneous head oscillation frequency (Hz) based on the current 
    oscillation amplitude and dominance.

    Parameters:
        A_t (float): Current oscillation amplitude in radians.
        dominance (float): Dominance value [-1, 1], where negative = submissive/nervous,
                           positive = confident/stable.
        A_max (float, optional): Maximum possible amplitude in radians. Defaults to 0.3.

    Returns:
        float: Instantaneous head oscillation frequency in Hz.

    Behavior:
        - Low dominance (negative) → faster, jittery, less controlled head movements.
        - High dominance (positive) → slower, smoother, confident head movements.
        - Frequency is inversely related to current amplitude:
            larger swings → slower oscillations, smaller swings → faster oscillations.
    """
    # Normalize dominance to [-1, 1] (-1 = negative/submissive, 1 = positive/confident)
    dom_norm = signed_norm("Dominance", dominance)

    # Base frequency range (Hz)
    f_min_base = 0.5  # slow, confident
    f_max_base = 2.0  # fast, nervous

    if dom_norm >= 0:
        # Confident: slower, controlled
        f_min = f_min_base
        f_max = f_min_base + (f_max_base - f_min_base) * (1 - dom_norm)
    else:
        # Submissive: faster, jittery
        f_min = f_min_base + (f_max_base - f_min_base) * (-dom_norm)
        f_max = f_max_base

    # Adjust frequency according to current amplitude
    A_ratio = np.clip(A_t / A_max, 0.0, 1.0)
    f_t = f_min + (f_max - f_min) * A_ratio  # larger amplitude → higher frequency

    return f_t