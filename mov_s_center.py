import numpy as np

def mov_s_center(pleasure: float, arousal: float, dominance: float) -> tuple[float, float, float, float, float]:
    """
    Détermine le centre du mouvement 
    Le pleasure influence le pitch_center (tête vers le haut/bas)
    La dominance influence le z_center (tente sortie/rentrée), le x_center (tête avant /arrière), et le yaw_center (tête légèrement tournée)
    L'arousal sert de facteur pour savoir à quel point le mouvement est loin du centre neutre.
    """
    # NORMALISATION DES VALEURS
        # dom_norm et pleasure_norm sont signés
    dominance_clipped = np.clip(dominance, -0.5, 0.5)
    dom_norm = abs(dominance_clipped) / 0.5 # → [0, 1]

    pleasure_clipped = np.clip(pleasure, -0.8, 0.8)
    pleasure_norm = pleasure_clipped / 0.8  # → [-1, 1]

        # arousal_norm est une intensité
    arousal_clipped = np.clip(arousal, -0.7, 0.7)
    arousal_norm = (arousal_clipped + 0.7) / 1.4 # → [0, 1]

    # On commence par le z_center car ses valeurs max/min ne dépendent pas des autres axes (valeurs en m)
    # A partir de -0.025 les mouvements sont très limités
    z_min=-0.050 
    z_max=0.025

    if dominance >= 0:
        # tête vers le haut
        z_center = z_max * dom_norm * arousal_norm
    else:
        # tête vers le bas
        z_center = z_min * dom_norm * arousal_norm

    # Pour la suite, on a besoin de la normalisation de z_center, en tenant compte de l'asymétrie
    if z_center >= 0:
        z_norm = abs(z_center) / z_max      # [0,1]
    else:
        z_norm = abs(z_center) / abs(z_min) # [0,1]

    # --- On fixe mtn le x-center (en m) ---
        # x = [-0.15,0.15] mais il faut vrmt éviter d'aller au delà que [-0.1,0.1]
        # Un peu pareil que pour z mais là en gros plus z est loin d'être à 0 et plus l'invervalle de x se réduit
    x_max_abs = 0.10
    # On se sert du z_norm comme facteur de compression
    x_reduction = (1.0 - z_norm ) ** 1.5
    x_max_eff = x_max_abs * x_reduction
    x_center  = np.sign(dominance) * x_max_eff * dom_norm * arousal_norm
    
    # --- Après tout ça on fixe le yaw center (en degrés) ---
        # yaw_min = [-25, 25] sauf si z_center < -0.025. Enfin l'idée c'est pas juste de mettre un if, il faut que l'intervalle de yaw se réduise progressivement quand z_center diminue.
        # Le plus petit intervalle de yaw est [-3,3]
        # Reachy ne tourne la tête que s'il ne veut pas affronter la situation = que si dominance < 0
        # La direction du yaw est choisie aléatoirement
    yaw_side = np.random.choice([-1.0, 1.0])
    
    # Par défaut yaw_center = 0
    yaw_center = 0.0

    if dominance < 0:
        yaw_max_abs = 25.0
        yaw_min_abs = 3.0

        yaw_reduction = (1.0 - z_norm) ** 2
        yaw_max_eff = yaw_min_abs + (yaw_max_abs - yaw_min_abs) * yaw_reduction

        yaw_center = (
            yaw_side          # gauche ou droite (aléatoire)
            * yaw_max_eff
            * (1.0 - dom_norm)     # dominance faible → grand yaw
            * arousal_norm    # arousal faible → peu expressif
        )

    # --- On fini par le pitch center (en degrés) ---
            # Là encore ça dépend du z_center. 
            # Plus z_center est loin de zéro, plus le pitch_center doit être bas aussi. Le plus petit intervalle de pitch est [-5, 5]
            # l'intervalle max de pitch c'est [-40, 30]. Donc pas symétrique.
            # Ne pas oublier de faire aussi intervenir l'arousal
    pitch_min = -40.0 # pitch négatif = tête vers le haut
    pitch_max =  30.0 # pitch positif = tête vers le bas

    pitch_min_neutral = -5.0
    pitch_max_neutral =  5.0

    pitch_reduction = (1.0 - z_norm) ** 1.5

    pitch_min_eff = (
        pitch_min_neutral
        + (pitch_min - pitch_min_neutral) * (1.0 - pitch_reduction)
    )

    pitch_max_eff = (
        pitch_max_neutral
        + (pitch_max - pitch_max_neutral) * (1.0 - pitch_reduction)
    )

    if pleasure_norm >= 0:
        # tête vers le haut → pitch négatif
        pitch_center = pitch_min_eff * pleasure_norm * arousal_norm
    else:
        # tête vers le bas → pitch positif
        pitch_center = -pitch_max_eff * pleasure_norm * arousal_norm

    return x_center, z_center, pitch_center, yaw_center, z_norm