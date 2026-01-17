import numpy as np
from normalsiation_PAD.norm import positive_norm

def ant_amplitude(dominance: float, center: float) -> float:
    """
    Calcule l'amplitude maximale du mouvement des antennes en fonction 
    de la dominance et du centre (décalé par la valence), 
    en respectant la limite [0, 3.16].

    dominance [-0.5,0.5] → facteur amplitude
    center [0, 3.16] → position moyenne
    """
    # Normalisation dans [0,1]
    dominance_norm = positive_norm("Dominance", dominance)

    # Amplitude physique max possible pour ce centre
    A_phys_max = min(center, 3.16 - center)
    
    # Appliquer dominance
    A_max = A_phys_max * dominance_norm
    return A_max