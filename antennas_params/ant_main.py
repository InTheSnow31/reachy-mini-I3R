import numpy as np
import time
from timestep import timestep

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
from .ant_center import ant_center
from .ant_angles import ant_angles

def main(pleasure: float = 0.0,
        arousal: float = 0.0,
        dominance: float = 0.0,
        duration: float = 5.0) -> None:
    """
    Fonction pour tester le mouvement des antennes isolément.
    Reste du corps en position neutre.

    Args: PAD values
    """
    dt = timestep(pleasure, arousal)
    center = ant_center(pleasure)

    with ReachyMini(media_backend="no_media") as mini:

        # Sign modifie la direction que prennent les antennes pour aller au centre
            # Dominance positive → antennes s'écartent vers l'extérieur
            # Dominance négative → antennes se rapprochent vers l'intérieur
        sign = -1 if dominance >= 0 else 1

        mini.goto_target( 
            antennas=[sign * center, -sign * center],
            head= create_head_pose(), # Position neutre de la tête
            duration=1.0,
            body_yaw=0.0
        ) 
    
        try:
            t0 = time.time()
            t = time.time() - t0

            while t <= duration:
                antennas_angles = ant_angles(
                    center=center,
                    pleasure=pleasure,
                    dominance=dominance,
                    t=t
                )
                mini.set_target(antennas=antennas_angles)

                time.sleep(dt)
                t += dt

        except KeyboardInterrupt:
            print("¡¡ Interruption détectée !!")

        finally:
            # Remise en position neutre avant de quitter
            mini.goto_target(
                antennas=[0.0, 0.0],
                head=create_head_pose(),
                duration=0.5
            )
            print("Fin du mouvement des antennes.")

if __name__ == "__main__":
    main()