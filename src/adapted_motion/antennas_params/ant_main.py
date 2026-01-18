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
    Tests antennas motion in isolation.

    The rest of the robot remains in a neutral posture.
    This function is intended for debugging and tuning.

    Args:
        pleasure: PAD pleasure value
        arousal: PAD arousal value
        dominance: PAD dominance value
        duration: motion duration in seconds
    """
    dt = timestep(arousal)
    center = ant_center(pleasure)

    with ReachyMini(media_backend="no_media") as mini:

        # Sign changes the direction the antennas take to reach the center
            # Positive dominance → antennas move outwards
            # Negative dominance → antennas move inwards
        sign = -1 if dominance >= 0 else 1

        mini.goto_target( 
            antennas=[sign * center, -sign * center],
            head= create_head_pose(), # Head in neutral position
            duration=1.0,
            body_yaw=0.0
        ) 
    
        try:
            t0 = time.time()
            t = time.time() - t0

            while t <= duration:
                antennas_angles = ant_angles(
                    pleasure=pleasure,
                    arousal=arousal,
                    dominance=dominance,
                    t=t
                )
                mini.set_target(antennas=antennas_angles)

                time.sleep(dt)
                t += dt

        except KeyboardInterrupt:
            print("¡¡ Interruption détectée !!")

        finally:
            # Return to neutral position before exiting
            mini.goto_target(
                antennas=[0.0, 0.0],
                head=create_head_pose(),
                duration=0.5
            )
            print("Fin du mouvement des antennes.")

if __name__ == "__main__":
    main()