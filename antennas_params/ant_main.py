import numpy as np
import time
from reachy_mini import ReachyMini
import timestep

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