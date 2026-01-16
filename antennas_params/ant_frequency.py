import numpy as np

def frequency_from_pleasure(pleasure: float, t: float) -> float:
    """
    Retourne une fréquence instantanée (Hz) dépendant uniquement du pleasure.
    Combine :
    - fréquence moyenne
    - légère modulation de fluidité (micro-irrégularités)
    """

    # Clamp réaliste
    pleasure_clipped = np.clip(pleasure, -0.8, 0.8)

    # Normalisation [-0.8,0.8] → [0,1]
    p = (pleasure_clipped + 0.8) / 1.6

    # --- fréquence moyenne (sûre) ---
    f_min = 0.05   # lent
    f_max = 0.90   # vivant
    f_base = f_min + (f_max - f_min) * p

    # --- fluidité : micro-variation temporelle ---
    # Pleasure bas → quasi aucune modulation
    # Pleasure haut → léger tremblement vivant
    mod_depth = 0.08 * p          # max ±8%
    mod_freq  = 1.2               # Hz (lent, organique)

    f_t = f_base * (1 + mod_depth * np.sin(2 * np.pi * mod_freq * t))

    return f_t