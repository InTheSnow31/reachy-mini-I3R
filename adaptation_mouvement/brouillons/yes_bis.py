import time

import numpy as np
from scipy.spatial.transform import Rotation as R

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
from mov_params.mov_s_center import mov_s_center

def main(pleasure: float, arousal: float, dominance: float) -> None:
    print("YES movement adapted with PAD values")

    with ReachyMini(media_backend="no_media") as reachy_mini:
        
        # --- CENTRES DU MOUVEMENT ---
        x_center, z_center, pitch_center, yaw_center = mov_s_center(pleasure, arousal, dominance)
        
        # --- POSE NEUTRE DE DEBUT ---
        reachy_mini.goto_target(
            create_head_pose(x = x_center, z=z_center, pitch=pitch_center, yaw=yaw_center), 
            # antennas=[0.0, 0.0],
            duration=1.0)

        # --- PARAMETRES DU MOUVEMENT ---
        amplitude = 0.25     # radians
        amplitude_deg = np.rad2deg(amplitude)  # convertir en degrés
        frequency = 0.6      # Hertz

        try:
            t0 = time.time()
            while True:
                t = time.time() - t0

                # --- OSCILLATION PITCH AUTOUR DU CENTRE ---
                angle = amplitude_deg * np.sin(2 * np.pi * frequency * t)
                pitch = pitch_center + angle  # pitch_center en degrés
                
                pose = create_head_pose(
                    x = x_center, 
                    z=z_center, 
                    pitch=pitch, 
                    yaw=yaw_center
                    )

                reachy_mini.set_target(head=pose)
                time.sleep(0.01)

        except KeyboardInterrupt:
            print("\nStopping motion and returning to neutral pose.")
            reachy_mini.goto_target(np.eye(4), duration=1.0)


if __name__ == "__main__":
    main()