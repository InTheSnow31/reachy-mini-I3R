import numpy as np

def ant_amplitude(dominance: float, center: float) -> float:
    """
    Calcule l'amplitude maximale des antennes en fonction de la dominance
    et du centre (décalé par la valence), en respectant la limite [0, 3.16].
    
    dominance [-1,1] → facteur amplitude
    center [0, 3.16] → position moyenne
    """
    # Clamp pour sécurité
    dominance_clipped = np.clip(dominance, -0.5, 0.5) # On ne va pas jusqu'à 1 car la dominance est rarement extrême (en tous cas pour les émotions de base)
    
    # Normalisation [-0.5,0.5] → [0,1]
    dominance_norm = (dominance_clipped + 0.5) / 1.0
    
    # Amplitude physique max possible pour ce centre
    A_phys_max = min(center, 3.16 - center)
    
    # Appliquer dominance
    A_max = A_phys_max * dominance_norm
    return A_max