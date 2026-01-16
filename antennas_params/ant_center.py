import numpy as np

def antennas_center(pleasure: float, min_angle=0.0, max_angle=3.16) -> float:
    """
    Déplace le centre du mouvement des antennes selon la valence (pleasure)
    max_offset : décalage max possible en rad
    """
    # Clamp des valeurs réalistes
    pleasure_clipped = np.clip(pleasure, -0.9, 0.9)

    # Normalisation [-0.9, 0.9] -> [0,1]
    pleasure_norm = (pleasure_clipped + 0.9) / 1.8  # 0 = -0.9, 1 = +0.9

    # On inverse pour que plaisir négatif → grand offset (= antennes basses)
    offset = max_angle - (pleasure_norm * (max_angle - min_angle))
    
    return offset