import time
import numpy as np
from scipy.spatial.transform import Rotation as R

from reachy_mini import ReachyMini
# from main_movement import oscillate_reachy
from reachy_mini.utils import create_head_pose

from prompt_emotion_PAD import get_emotion_PAD
from prompt_duration import get_duration

from timestep import main as timestep

from antennas_params import ant_angles, ant_center
from mov_params.mov_s_center import mov_s_center
from mov_params.mov_amplitude import main as mov_amplitude
from mov_params.mov_frequency import mov_frequency
from mov_params.amp_max_mov import amp_max_yes

pleasure, arousal, dominance = get_emotion_PAD()
duration = get_duration()
# yes==True # choix du mouvement YES / NO

# --- CENTRES DU MOUVEMENT ---
x_center, z_center, pitch_center, yaw_center, z_norm = mov_s_center(pleasure, arousal, dominance)
base_antennas = ant_center.antennas_center_from_pleasure(pleasure)

amp_max = amp_max_yes(
    arousal=arousal,
    z_norm=z_norm
)
# print(f"Amplitude max YES selon arousal et z_norm : {amp_max:.3f} rad et en degrees : {np.degrees(amp_max):.1f}°")
dt = timestep(pleasure, arousal)

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
            amplitude = mov_amplitude(t, arousal, dominance, amp_max, duration)     # radians
            frequency = mov_frequency(amplitude, pleasure, amp_max)      # Hertz
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
            antennas_angles = ant_angles.antennas_angles_according_to_PAD(
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
        print("✊ Interruption prolétarienne détectée")
        mini.goto_target(
            np.eye(4),
            antennas=[0.0, 0.0], 
            duration=0.5
        )


# Exemple d'utilisation de la fonction oscillate_reachy

# Crée l’instance du robot
# with ReachyMini() as mini:
#     # Appelle la fonction avec l'instance et éventuellement tes paramètres
#     oscillate_reachy(
#         mini,
#         duration=15.0,   # temps total du mouvement en secondes
#         amplitude=0.1,   # amplitude du va-et-vient en m
#         speed=2,         # nombre d'alternances par seconde
#         smoothness=0.5   # fluidité du mouvement (fraction du temps de transition)
#     )

# with ReachyMini() as mini:
#     # Look up and tilt head
#     mini.goto_target(
#         head=create_head_pose(z=10, roll=15, degrees=True, mm=True),
#         duration=1.0
#     )

# yes.main(pleasure, arousal, dominance)


    # mini.goto_target(antennas=[0.0, 0.0], duration=1.0)
    # mini.goto_target(antennas=[1.0, -1.0], duration=1.0)
    # mini.goto_target(antennas=[3.0, -3.0], duration=1.0)
    # mini.goto_target(antennas=[2.8, -2.8], duration=1.0)
    # mini.goto_target(antennas=[0.0, 0.0], duration=1.0)

    # mini.goto_target(antennas=[-1.0, 1.0], duration=1.0)
    # mini.goto_target(antennas=[-2.8, 2.8], duration=1.0)
    # mini.goto_target(antennas=[-3.0, 3.0], duration=1.0)
    # mini.goto_target(antennas=[-2.8, 2.8], duration=1.0)
    # mini.goto_target(antennas=[0.0, 0.0], duration=1.0)

# antennas_according_to_PAD(
#     pleasure=pleasure,
#     arousal=arousal,
#     dominance=dominance,
#     t=t0
# )


# with ReachyMini(media_backend="no_media") as reachy_mini:
#     reachy_mini.goto_target(
#             create_head_pose(x=0, y=0,z=30, roll=0, pitch=0,yaw=-40, degrees=True, mm=True), 
#             antennas=[0.0, 0.0], 
#             duration=1.0)

#emotive_yes_no.main()