import numpy as np
from normalsiation_PAD.norm import positive_norm

def ant_center(pleasure: float, min_angle=0.0, max_angle=3.16) -> float:
    """
    Déplace le centre du mouvement des antennes selon la valence (pleasure)
    max_offset : décalage max possible en rad
    """
    # Normalisation dans [0,1]
    pleasure_norm = positive_norm("Pleasure", pleasure)

    # On inverse pour que plaisir négatif → grand offset (= antennes basses)
    offset = max_angle - (pleasure_norm * (max_angle - min_angle))
    
    return offset