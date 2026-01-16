import numpy as np
from .ant_amplitude import ant_amplitude
from .ant_frequency import ant_frequency

def ant_angles(center: float = 0.0,
                pleasure: float = 0.0,
                dominance: float = 0.0,
                t: float = 0.0) -> list[float]:
    """
    Retourne les angles des antennes selon PAD à un instant t.

    Args:
        base_angles: position neutre des antennes [right, left] en rad
        pleasure: influence la vitesse
        arousal: influence la fluidité/saccade
        dominance: influence l'amplitude
        t: temps écoulé (s)

    Returns:
        angles des antennes [right, left] en rad
    """
    # --- paramètres mouvement ---
    A_max = ant_amplitude(dominance, center) 
    f_t = ant_frequency(pleasure, t)

    # --- calcul angles ---
    angle = A_max * np.sin(2 * np.pi * f_t * t)

    # antennes symétriques selon dominance : 
    if dominance >= 0:
        right_angle = - center - angle
        left_angle  = center + angle
    if dominance < 0:
        right_angle = center + angle
        left_angle  = - center - angle
    # En plus de l'amplitude, la dominance a un impact sur le coté tourné vers l'extérieur/intérieur du mouvement

    return [right_angle, left_angle]