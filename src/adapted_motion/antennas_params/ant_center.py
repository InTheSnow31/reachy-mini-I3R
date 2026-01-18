import numpy as np
from adapted_motion.normalisation_PAD.norm import positive_norm

def ant_center(pleasure: float, min_angle=0.0, max_angle=3.16) -> float:
    """
    Shifts the antennas motion center based on valence (pleasure).

    A positive pleasure shifts the center upward,
    while a negative pleasure shifts it downward.

    Args:
        pleasure: valence value
        min_angle: lower bound of antennas angle (rad)
        max_angle: upper bound of antennas angle (rad)

    Returns:
        Center angle of the antennas motion (rad)
    """
    # Normalization in [0, 1]
    pleasure_norm = positive_norm("Pleasure", pleasure)

    # Invert mapping so low pleasure → large offset (antennas down)
    offset = max_angle - (pleasure_norm * (max_angle - min_angle))
    
    return offset