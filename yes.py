"""Reachy Mini example that plays yes motions driven by a sine wave."""

import time
# from typing import Literal

import numpy as np
from scipy.spatial.transform import Rotation as R

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
from mov_amplitude import main as mov_amplitude
from mov_frequency import main as mov_frequency


def main(pleasure: float, arousal: float, dominance: float, duration: float) -> None:
    print("YES movement adapted with PAD values")

    with ReachyMini(media_backend="no_media") as reachy_mini:
        decay_time = duration     # temps total
        dt = 0.01

        # POSE NEUTRE DEBUT
        reachy_mini.goto_target(np.eye(4), antennas=[0.0, 0.0], duration=1.0)
        pose = np.eye(4)
        base_antennas = [0.0, 0.0]

        # Pleasure : énergie / vitesse

        # Arousal : fluidité / saccadé
        def arousal_modulation(t, arousal):
            """
            arousal positif → saccadé → on ajoute une modulation sinus sur la fréquence
            arousal négatif → plus fluide → modulation faible
            """
            mod_strength = max(0.0, arousal)  # ∈ [0,1] si arousal positif
            mod = 1 + 0.2 * mod_strength * np.sin(2 * np.pi * 3 * t)  # 3 Hz saccade
            return mod

        # --- boucle de mouvement ---
        try:
            t0 = time.time()
            while True:
                t = time.time() - t0
                # if t >= decay_time:
                #     break

                amplitude = mov_amplitude(t, dominance)
                f_t = mov_frequency(amplitude, pleasure)

                # modulation fluidité selon arousal
                f_t *= arousal_modulation(t, arousal)

                # calcul de l'angle (sinus)
                angle = amplitude * np.sin(2 * np.pi * f_t * t)

                # rotation pitch only
                euler_rot = np.array([0.0, angle, 0.0])
                pose[:3, :3] = R.from_euler("xyz", euler_rot, degrees=False).as_matrix()

                reachy_mini.set_target(head=pose, antennas=base_antennas)
                time.sleep(dt)

        except KeyboardInterrupt:
            print("\nStopping motion and returning to neutral pose.")
            reachy_mini.goto_target(np.eye(4), antennas=base_antennas, duration=1.0)


if __name__ == "__main__":
    main()