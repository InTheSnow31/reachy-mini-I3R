import numpy as np
from adapted_motion.normalisation_PAD.norm import positive_norm, signed_norm

def head_s_center(pleasure: float, arousal: float, dominance: float) -> tuple[float, float, float, float, float]:
    """
    Compute the central reference positions for head movement.

    Parameters influence the movement as follows:
    - Pleasure: modulates pitch_center (vertical tilt of the head)
    - Dominance: modulates z_center (forward/back tilt), x_center (forward/back translation), and yaw_center (lateral rotation)
    - Arousal: scales the deviation from the neutral/central posture, affecting movement intensity

    Returns:
        Tuple containing (x_center, z_center, pitch_center, yaw_center, z_norm)
    """
    # --- NORMALIZATION OF VALUES ---
    pleasure_norm = signed_norm("Pleasure", pleasure)  # → [-1, 1]
    arousal_norm  = positive_norm("Arousal", arousal)  # → [0, 1], intensity
    dom_norm      = positive_norm("Dominance", dominance)  # → [0, 1], intensity

    # --- Z CENTER (m) ---
    # Max/min values independent of other axes
    z_min = -0.050  # extreme downward tilt
    z_max = 0.025   # extreme upward tilt

    if dominance >= 0:
        # Head tilts upward
        z_center = z_max * dom_norm * arousal_norm
    else:
        # Head tilts downward
        z_center = z_min * dom_norm * arousal_norm

    # Normalized z_center accounting for asymmetry
    if z_center >= 0:
        z_norm = abs(z_center) / z_max      # [0,1]
    else:
        z_norm = abs(z_center) / abs(z_min) # [0,1]

    # --- X CENTER (m) ---
    # X range: [-0.15, 0.15], but limit to [-0.1, 0.1]
    # The further z is from 0, the smaller the x range
    x_max_abs = 0.10
    x_reduction = (1.0 - z_norm) ** 1.5  # compression factor
    x_max_eff  = x_max_abs * x_reduction
    x_center   = np.sign(dominance) * x_max_eff * dom_norm * arousal_norm

    # --- YAW CENTER (degrees) ---
    # Default yaw = 0
    yaw_center = 0.0
    yaw_side   = np.random.choice([-1.0, 1.0])  # random left/right

    if dominance < 0:
        # Head turns to avoid / submissive behavior
        yaw_max_abs = 25.0
        yaw_min_abs = 3.0
        yaw_reduction = (1.0 - z_norm) ** 2
        yaw_max_eff = yaw_min_abs + (yaw_max_abs - yaw_min_abs) * yaw_reduction

        yaw_center = (
            yaw_side               # left or right
            * yaw_max_eff
            * (1.0 - dom_norm)     # low dominance → larger yaw
            * arousal_norm         # low arousal → less expressive
        )

    # --- PITCH CENTER (degrees) ---
    # Pitch depends on z_center. Further from 0 → lower pitch
    pitch_min = -40.0   # negative pitch = head up
    pitch_max = 30.0    # positive pitch = head down
    pitch_min_neutral = -5.0
    pitch_max_neutral = 5.0

    pitch_reduction = (1.0 - z_norm) ** 1.5

    pitch_min_eff = pitch_min_neutral + (pitch_min - pitch_min_neutral) * (1.0 - pitch_reduction)
    pitch_max_eff = pitch_max_neutral + (pitch_max - pitch_max_neutral) * (1.0 - pitch_reduction)

    if pleasure_norm >= 0:
        # Head up → negative pitch
        pitch_center = pitch_min_eff * pleasure_norm * arousal_norm
    else:
        # Head down → positive pitch
        pitch_center = -pitch_max_eff * pleasure_norm * arousal_norm

    return x_center, z_center, pitch_center, yaw_center, z_norm