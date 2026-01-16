from .params import BOUNDS

def positive_norm(param_type: str, value: float) -> float:
    """
    Normalise un paramètre dans [0,1] selon son type et ses bornes.
    """
    min_val, max_val = BOUNDS[param_type]

    # clipping
    value_clipped = max(min_val, min(max_val, value))

    # normalisation linéaire dans [0,1]
    return (value_clipped - min_val) / (max_val - min_val)

def signed_norm(param_type: str, value: float) -> float:
    """
    Normalise un paramètre dans [-1,1] selon son type et ses bornes.
    """
    min_val, max_val = BOUNDS[param_type]
    value_clipped = max(min_val, min(max_val, value))
    return 2 * ((value_clipped - min_val) / (max_val - min_val)) - 1