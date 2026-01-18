import numpy as np
from normalisation_PAD.norm import positive_norm, signed_norm

def head_amplitude(t, pleasure, dominance, A_phys_max, duration):
    """
    Compute the head oscillation amplitude over time for Reachy.

    This function generates smooth, expressive head movements whose intensity
    and temporal evolution depend on the robot's "emotional state".

    Parameters:
        t (float): Current time in seconds. Determines how far we are
                   into the movement (used for crescendo/decrescendo effects).
        pleasure (float): Pleasure/valence [-1, 1]. 
                          Absolute value controls movement amplitude:
                          - Neutral (~0) → small, subtle movements
                          - Extreme (~±1) → large, expressive movements
        dominance (float): Dominance [-1, 1].
                          - Positive → crescendo (amplitude rises toward end)
                          - Negative → decrescendo (amplitude fades out)
                          Also modulates maximum amplitude slightly.
        A_phys_max (float): Physical maximum amplitude allowed for the current pose (radians).
                            The amplitude will never exceed this value.
        duration (float): Total movement duration (seconds), used to scale
                          growth/decay phases smoothly.

    Returns:
        float: Instantaneous head oscillation amplitude (radians).

    Notes:
        - Uses sine/cosine smoothing to avoid abrupt starts or stops.
        - Amplitude depends on pleasure for expressiveness and dominance for motion shaping.
        - All outputs are in radians.
    """

    # --- TIME-BASED GROWTH FACTOR ---
    pleasure_norm = positive_norm("Pleasure", pleasure)  # How 'excited' the emotion is
    min_ratio = 0.1
    max_ratio = 0.5
    
    # Higher pleasure → quicker growth (expressive emotions act fast!)
    growth_ratio = max_ratio - pleasure_norm * (max_ratio - min_ratio)
    
    # Effective growth time in seconds
    growth_time = duration * growth_ratio

    # --- DOMINANCE MODULATION ---
    dom_norm = signed_norm("Dominance", dominance)  # [-1, 1], how confident the robot feels
    factor = 0.6 + 0.4 * (dom_norm + 1) / 2  # Scale max amplitude to avoid extremes
    A_max = A_phys_max * factor  # Actual max amplitude for this motion

    # --- AMPLITUDE CALCULATION OVER TIME ---
    if t >= duration:
        # End of movement → zero amplitude
        return 0.0

    if dominance >= 0:
        # Crescendo: amplitude rises smoothly to A_max
        if t < growth_time:
            # Smooth start with sine curve for organic growth
            return A_max * np.sin(np.pi/2 * (t / growth_time))
        else:
            # Hold maximum amplitude for confident motions
            return A_max
    else:
        # Decrescendo: amplitude starts high and fades out
        if t < growth_time:
            # Initial plateau at A_max for subtle initial expression
            return A_max
        else:
            # Smooth decay using cosine, ends gently at 0
            decay_progress = (t - growth_time) / (duration - growth_time)
            decay_progress = np.clip(decay_progress, 0.0, 1.0)
            # cos(pi/2 * 0) = 1 → start at A_max ; cos(pi/2 * 1) = 0 → end at 0
            return A_max * np.cos(np.pi/2 * decay_progress)