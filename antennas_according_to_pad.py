import numpy as np
import time
from reachy_mini import ReachyMini
import timestep

def antennas_center_from_pleasure(pleasure: float, min_angle=0.0, max_angle=3.16) -> float:
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

def amplitude_antennes(dominance: float, center: float) -> float:
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

def antennas_angles_according_to_PAD(  center: float = 0.0,
                              pleasure: float = 0.0,
                              dominance: float = 0.0,
                              t: float = 0.0) -> list[float]:
    """
    Retourne les angles des antennes selon PAD à un instant t.

    Args:
        base_angles: position neutre des antennes [right, left] en rad
        pleasure: [-1,1], influence la vitesse
        arousal: [-1,1], influence la fluidité/saccade
        dominance: [-1,1], influence l'amplitude
        t: temps écoulé (s)

    Returns:
        angles des antennes [right, left] en rad
    """
     

    # --- paramètres mouvement ---
    A_max = amplitude_antennes(dominance, center) 
    f_t = frequency_from_pleasure(pleasure, t)

    # --- calcul angles ---
    angle = A_max * np.sin(2 * np.pi * f_t * t)

    # antennes symétriques selon dominance : 
    if dominance >= 0:
        right_angle = - center - angle
        left_angle  = center + angle
    if dominance < 0:
        right_angle = center + angle
        left_angle  = - center - angle
    # En plus de l'amplitude, la dominance a un impact sur le coté tourné vers l'extérieur/intérieur du mouvement

    return [right_angle, left_angle]

def main(pleasure: float = 0.0,
        arousal: float = 0.0,
        dominance: float = 0.0,
        t: float = 0.0):
    
    t0 = time.time()
    center = antennas_center_from_pleasure(pleasure)

    with ReachyMini(media_backend="no_media") as mini:
        sign = -1 if dominance >= 0 else 1
        mini.goto_target( 
            antennas=[sign * center, -sign * center], 
            duration=1.0) # !!!!!! Quand on couplera le corps et les antennes, penser à retirer la position du corps ici !!!!!!
    
        try:
            while True:
                t = time.time() - t0

                antennas_angles = antennas_angles_according_to_PAD(
                    center=center,
                    pleasure=pleasure,
                    dominance=dominance,
                    t=t
                )
                mini.set_target(antennas=antennas_angles)

                dt = timestep(arousal)
                time.sleep(dt)

        except KeyboardInterrupt:
            print("✊ Interruption prolétarienne détectée")
            mini.goto_target(antennas=[0.0, 0.0], duration=0.5)

if __name__ == "__main__":
    main()