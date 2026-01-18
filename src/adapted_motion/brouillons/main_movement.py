import time
import numpy as np
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

def oscillate_reachy(mini, duration=10.0, amplitude=0.1, speed=2, smoothness=0.5):
    """
    Déplace le robot entre deux directions puis revient à la position neutre.

    mini: ReachyMini instance
    duration: temps total du mouvement en secondes
    amplitude: distance maximale du va-et-vient (en m)
    speed: nombre d'alternances par seconde
    smoothness: fraction de temps pour effectuer le mouvement (0 < smoothness <= 1)
    """
    # Positions
    neutral_pos = np.array([0.0, 0.0, 0.0])       # Position neutre x, y, z
    dir1 = np.array([amplitude, 0.0, 0.0])       # Direction 1
    dir2 = np.array([-amplitude, 0.0, 0.0])      # Direction 2

    # Durée par transition
    period = 1 / speed                             # Temps pour changer de direction
    move_time = period * smoothness                # Temps pour effectuer la transition
    idle_time = period * (1 - smoothness)          # Temps où il reste immobile avant de changer de direction

    t0 = time.time()
    end_time = t0 + duration

    # Début au neutre
    mini.goto_target(create_head_pose(), duration=move_time)

    current_dir = 0  # 0 -> dir1, 1 -> dir2
    next_change = t0

    try:
        while time.time() < end_time:
            now = time.time()

            if now >= next_change:
                # Déterminer la prochaine position
                if current_dir == 0:
                    target_pos = dir1
                    current_dir = 1
                else:
                    target_pos = dir2
                    current_dir = 0

                mini.goto_target(target_pos, duration=move_time)
                next_change = now + period

            time.sleep(0.01)

        # Retour à la position neutre
        mini.goto_target(neutral_pos, duration=move_time)

    except KeyboardInterrupt:
        mini.goto_target(neutral_pos, duration=move_time)
        print("Mouvement interrompu, retour à la position neutre")
