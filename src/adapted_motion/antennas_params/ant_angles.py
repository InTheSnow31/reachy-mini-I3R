import numpy as np
from .ant_amplitude import ant_amplitude
from .ant_frequency import ant_frequency
from .ant_center import ant_center

def ant_angles(pleasure: float = 0.0,
                arousal: float = 0.0,
                dominance: float = 0.0,
                t: float = 0.0) -> list[float]:
    """
    Computes antennas angles at time t based on PAD values.

    Args:
        pleasure: helps define the center of the movement
        arousal: controls motion amplitude
        dominance: control inward / outward movement
        t: elapsed time in seconds

    Returns:
        Antennas angles [right, left] in radians
    """
    # --- motion's parameters ---
    center = ant_center(pleasure)
    A_max = ant_amplitude(arousal) 
    f_t = ant_frequency(dominance, t)

    # --- angle calculation ---
    angle = A_max * np.sin(2 * np.pi * f_t * t)

    # symetry according to dominance : 
    if dominance >= 0:
        right_angle = - center - angle
        left_angle  = center + angle
    if dominance < 0:
        right_angle = center + angle
        left_angle  = - center - angle

    return [right_angle, left_angle]