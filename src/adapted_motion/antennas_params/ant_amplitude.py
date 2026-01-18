import numpy as np
from adapted_motion.normalisation_PAD.norm import positive_norm

def ant_amplitude(arousal: float) -> float:
    """
    Computes the maximum antennas motion amplitude.

    The amplitude depends on:
    - Arousal: scales the motion intensity
    - Center position: shifted by valence (pleasure)

    The resulting value is clipped to the range [0, 3.16].

    Arousal range:
    - Arousal → amplitude scaling factor

    Center range:
    - center ∈ [0, 3.16] → mean antennas position
    """
    # Signed normalization in [-1, 1]
    arousal_norm = positive_norm("Arousal", arousal)
    
    # Apply arousal to amplitude
    amp_max = 3.0/2 # Amplitude maximal. If it's > 3.16/2 it will be too far appart from the center.
    amp = amp_max * arousal_norm

    # Always positive and greater than zero
    epsilon = 0.05  # minimum amplitude to ensure movement
    amp = max(abs(amp), epsilon)

    # Ensure it does not exceed the physical limit
    amp = min(amp, 3.16)

    return amp