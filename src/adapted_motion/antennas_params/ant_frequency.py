import numpy as np
from normalisation_PAD.norm import positive_norm

def ant_frequency(dominance: float, t: float) -> float:
    """
Returns an instantaneous frequency (Hz) driven only by pleasure.

The frequency combines:
- A mean oscillation frequency
- A small modulation to introduce fluidity variations
This creates subtle micro-irregularities without affecting stability.

Low dominance → small, quick, nervous movements
High dominance → slow, confident, fluid movements
"""
    # Normalization
    d = positive_norm("Dominance", dominance)

    # --- average (safe) frequency ---
    f_min = 0.05   # slow
    f_max = 0.5   # lively
    f_base = f_min + (f_max - f_min) * d

    # --- fluidity: temporal micro-variation ---
    mod_depth = 0.2 * ((1 - d)**2)  # more modulation if low dominance     
    mod_freq  = 1.2               # Hz (slow, organic)

    f_t = f_base * (1 + mod_depth * np.sin(2 * np.pi * mod_freq * t))

    return f_t