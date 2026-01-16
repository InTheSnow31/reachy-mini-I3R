import numpy as np

def amp_max_yes(
    arousal: float,
    z_norm: float,  # normalisé entre z_min et z_max
    A_max_neutral=np.pi/3,  # 60°
    A_min=0.175             # 10°
) -> float:
    """
    Calcule l’amplitude max du mouvement YES
    en fonction du z_center (pitch moyen) donc capacité physique à faire le mouvement
    ET de l'arousal

    Retourne une amplitude en radians
    """
    # amplification non linéaire aux extrêmes (inverse de avant)
    amplification = (1.0 - z_norm) ** 2
    amplification = np.clip(amplification, 0.0, 1.0)

    # Conversion en radians
    return A_min + (A_max_neutral - A_min) * amplification * (0.5 + 0.5 * arousal)

