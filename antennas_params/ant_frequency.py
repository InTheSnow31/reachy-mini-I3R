import numpy as np
from normalsiation_PAD.norm import positive_norm

def ant_frequency(pleasure: float, t: float) -> float:
    """
    Retourne une fréquence instantanée (Hz) dépendant uniquement du pleasure.
    Combine :
    - fréquence moyenne
    - légère modulation de fluidité (micro-irrégularités)
    """
    # Normalisation
    p = positive_norm("Pleasure", pleasure)

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