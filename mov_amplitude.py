import numpy as np

def main(t, arousal, dominance, A_phys_max, duration):
    """
    - dominance > 0 → crescendo (grande amplitude à la fin)
    - dominance < 0 → decrescendo (s’éteint)
    La dominance a également un impact sur l’amplitude maximale

    Tout est en radians
    """
    # --- CALCUL TEMPS DE CROISSANCE ---
    # Clamp arousal
    arousal_clipped = np.clip(arousal, -0.7, 0.7)
    min_ratio=0.1
    max_ratio=0.5
    
    # Mapping [-0.7,0.7] -> [max_ratio, min_ratio]
    # Plus arousal est élevé -> growth_time plus court
    growth_ratio = max_ratio - (arousal_clipped + 0.7)/1.4 * (max_ratio - min_ratio)
    
    # Growth_time effectif
    growth_time = duration * growth_ratio
    
    dominance_clipped = np.clip(dominance, -0.5, 0.5)
    dom_norm = dominance_clipped / 0.5 # → [-1, 1]

    # Amplitude max modulée par dominance (évite 0 ou x2 débiles)
    factor = 0.6 + 0.4 * (dom_norm + 1) / 2  # ∈ [0.6, 1.0]
    A_max = A_phys_max * factor
    
    # --- CALCUL AMPLITUDE SELON LE TEMPS ---
    # Fin du mouvement
    if t >= duration:
        return 0.0

    if dominance >= 0:
        # Crescendo
        if t < growth_time:
            # Phase de croissance douce (sin lisse)
            return A_max * np.sin(np.pi/2 * (t / growth_time))
        else:
            # Plateau stable à A_max
            return A_max
    else:
        # Decrescendo
        if t < growth_time:
            # Plateau initial à A_max
            return A_max
        else:
            # Décroissance douce avec cos, commence à A_max et descend à 0
            decay_progress = (t - growth_time) / (duration - growth_time)
            decay_progress = np.clip(decay_progress, 0.0, 1.0)
            # cos(pi/2 * 0) = 1 → commence à A_max ; cos(pi/2 * 1) = 0 → fini à 0
            return A_max * np.cos(np.pi/2 * decay_progress)