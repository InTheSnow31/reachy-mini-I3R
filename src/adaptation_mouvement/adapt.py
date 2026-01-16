import time
import numpy as np
from scipy.spatial.transform import Rotation as R

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

from prompts.prompt_emotion_PAD import get_emotion_PAD
from prompts.prompt_duration import get_duration

from timestep import timestep

from antennas_params.ant_main import main as antennas_main
from antennas_params.ant_angles import ant_angles
from antennas_params.ant_center import ant_center

from head_params.head_s_center import head_s_center
from head_params.head_amplitude import head_amplitude
from head_params.head_frequency import head_frequency
from head_params.head_amp_max import amp_max_yes

# --- SELECTION DES PARAMETRES EMOTIONNELS ET DUREE ---
pleasure, arousal, dominance = get_emotion_PAD()
duration = get_duration()

# --- TEST ANTENNES ISOLEES
# antennas_main(
#     pleasure=pleasure, 
#     arousal=arousal, 
#     dominance=dominance, 
#     duration=duration
# )

# --- CHOIX DU MOUVEMENT (YES / NO / ...) ---
# yes==True # choix du mouvement YES / NO

# --- CENTRES DU MOUVEMENT ---
x_center, z_center, pitch_center, yaw_center, z_norm = head_s_center(pleasure, arousal, dominance)
base_antennas = ant_center(pleasure)

amp_max = amp_max_yes(
    arousal=arousal,
    z_norm=z_norm
)
# print(f"Amplitude max YES selon arousal et z_norm : {amp_max:.3f} rad et en degrees : {np.degrees(amp_max):.1f}°")
dt = timestep(pleasure, arousal)

def main():

    with ReachyMini(media_backend="no_media") as mini:
        pose_center = create_head_pose(
            x=x_center,
            z=z_center,
            pitch=pitch_center,
            yaw=yaw_center
        )
        sign = -1 if dominance >= 0 else 1
        mini.goto_target( 
                head=pose_center,
                antennas=[sign * base_antennas, -sign * base_antennas], 
                duration=1.0)
        
        try:
            t0 = time.time()
            t = time.time() - t0
            while True:
                
                # --- OSCILLATION PITCH AUTOUR DU CENTRE ---
                amplitude = head_amplitude(t, arousal, dominance, amp_max, duration)     # radians
                frequency = head_frequency(amplitude, pleasure, amp_max)      # Hertz
                print(f"t={t:.2f} s - amp={amplitude:.3f} rad ({np.degrees(amplitude):.1f}°) - freq={frequency:.3f} Hz")

                angle = amplitude * np.sin(2 * np.pi * frequency * t)
                
                # rotation relative (YES)
                R_offset = R.from_euler("xyz", [0.0, angle, 0.0], degrees=False)

                # rotation centrale extraite
                R_center = R.from_matrix(pose_center[:3, :3])

                # composition : centre + oscillation
                R_total = R_center * R_offset

                pose = pose_center.copy()
                pose[:3, :3] = R_total.as_matrix()
                
                # --- MOUVEMENTS ANTENNES ---
                antennas_angles = ant_angles(
                    center=base_antennas,
                    pleasure=pleasure,
                    dominance=dominance,
                    t=t
                )            

                mini.set_target(
                    head=pose,
                    antennas=antennas_angles
                    )
                time.sleep(dt)
                t += dt  # incrément strict

        except KeyboardInterrupt:
            print("¡¡ Interruption détectée !!")
            mini.goto_target(
                np.eye(4),
                antennas=[0.0, 0.0], 
                duration=0.5
            )


if __name__ == "__main__":
    main()