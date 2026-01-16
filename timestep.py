import numpy as np

def main(pleasure: float, arousal: float) -> float:
    """
    - arousal bas → mouvement lent
    - arousal haut → mouvement rapide
    - pleasure proche de 0 → mouvement plus rapide
    - pleasure éloigné de 0 → mouvement plus posé
    Cela change en partie la fluidité du mouvement
    """
    arousal_clipped = np.clip(arousal, -0.7, 0.7)
    arousal_norm = (arousal_clipped + 0.7) / 1.4  # [0,1]

    # --- Pleasure ---
    pleasure_clipped = np.clip(pleasure, -0.8, 0.8)
    pleasure_norm = abs(pleasure_clipped) / 0.8  # [0,1], 0 = centre, 1 = extrêmes

    dt_min = 0.01   # rapide mais safe
    dt_max = 0.05   # lent, posé

    # combinaison : on veut que dt diminue si arousal ↑ ou pleasure proche de 0
    dt = dt_max - (arousal_norm * 0.7 + (1 - pleasure_norm) * 0.3) * (dt_max - dt_min)

    return np.clip(dt, dt_min, dt_max)

if __name__ == "__main__":
    main()