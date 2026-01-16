import numpy as np
from normalsiation_PAD.norm import positive_norm, signed_norm

def head_frequency(A_t, pleasure, arousal, A_max=0.3):
    """
    Calcul de la fréquence de mouvement en Hz
    A_t : amplitude actuelle (radians)
    pleasure : [-1, 1] -> modifie vitesse
    arousal : [-1, 1] -> modifie vitesse
    A_max : amplitude max possible (radians)
    """
    pleasure_norm = signed_norm("Pleasure", pleasure)  # → [-1, 1]
    arousal_norm = positive_norm("Arousal", arousal)  # → [0, 1]

    # Base frequency
    f_min_base = 0.5
    f_max_base = 2.0

    # Modulation selon pleasure
    pleasure_factor = 1.0 + 0.5 * pleasure_norm
    f_min = f_min_base * pleasure_factor
    f_max = f_max_base * pleasure_factor

    # Fréquence inversement proportionnelle à l'amplitude
    # plus l'amplitude est grande, plus la fréquence diminue
    A_ratio = np.clip(A_t / A_max, 0.0, 1.0)
    f_t = f_min + (f_max - f_min) * A_ratio

    # Ajout d'une modulation multiplicative selon l'arousal
    # arousal ≈ 0 → pas de modif, arousal ≈ 1 → fréquence augmentée jusqu'à +30%
    f_t *= 1.0 + 0.2 * arousal_norm

    return f_t