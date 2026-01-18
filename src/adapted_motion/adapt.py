# =========================
# LIBRARIES
# =========================
import time

# Scientific calculations
import numpy as np
from scipy.spatial.transform import Rotation as R

# Reachy Mini robot
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

# Prompts / cognitive parameters (PAD, duration)
from adapted_motion.prompts.prompt_motion_type import choose_motion
from adapted_motion.prompts.prompt_emotion_PAD import get_emotion_PAD
from adapted_motion.prompts.prompt_duration import get_duration

# Discrete time management
from adapted_motion.timestep import timestep

# Antennas
from adapted_motion.antennas_params.ant_main import main as antennas_main
from adapted_motion.antennas_params.ant_angles import ant_angles
from adapted_motion.antennas_params.ant_center import ant_center

# Head
from adapted_motion.head_params.head_s_center import head_s_center
from adapted_motion.head_params.head_amplitude import head_amplitude
from adapted_motion.head_params.head_frequency import head_frequency
from adapted_motion.head_params.head_amp_max import amp_max

def main():

    # --- MOTION CHOICE ---
    yes_motion = choose_motion()  # Returns True if YES, False if NO

    # --- SELECTION OF EMOTIONAL PARAMETERS AND DURATION ---
    pleasure, arousal, dominance = get_emotion_PAD()
    duration = get_duration()

    # --- TEST ISOLATED ANTENNAS ---
    # antennas_main(
    #     pleasure=pleasure, 
    #     arousal=arousal, 
    #     dominance=dominance, 
    #     duration=duration
    # )

    # --- MOTION CENTERS ---
    x_center, z_center, pitch_center, yaw_center, z_norm = head_s_center(pleasure, arousal, dominance)
    base_antennas = ant_center(pleasure)

    amp_max_head = amp_max(
        arousal=arousal,
        z_norm=z_norm,
        dominance=dominance
    )
    # print(f"Max amplitude YES according to arousal and z_norm: {amp_max:.3f} rad ({np.degrees(amp_max):.1f}°)")

    dt = timestep(arousal)

    with ReachyMini(media_backend="no_media") as mini:
        # Create central head pose
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
                
                # --- OSCILLATION AROUND CENTER ---
                amplitude = head_amplitude(t, pleasure, dominance, amp_max_head, duration)     # radians
                frequency = head_frequency(amplitude, dominance, amp_max_head)      # Hertz
                print(f"t={t:.2f} s - amp={amplitude:.3f} rad ({np.degrees(amplitude):.1f}°) - freq={frequency:.3f} Hz")

                angle = amplitude * np.sin(2 * np.pi * frequency * t)
                
                # --- relative rotation: YES or NO ---
                if yes_motion:
                    # YES → oscillate around pitch (head nod)
                    R_offset = R.from_euler("xyz", [0.0, angle, 0.0], degrees=False)
                else:
                    # NO → oscillate around roll (head shake)
                    R_offset = R.from_euler("xyz", [0.0, 0.0, angle], degrees=False)

                # central rotation extracted from pose
                R_center = R.from_matrix(pose_center[:3, :3])

                # combine center + oscillation
                R_total = R_center * R_offset

                pose = pose_center.copy()
                pose[:3, :3] = R_total.as_matrix()
                
                # --- ANTENNA MOVEMENTS ---
                antennas_angles = ant_angles(
                    pleasure=pleasure,
                    arousal=arousal,
                    dominance=dominance,
                    t=t
                )            

                mini.set_target(
                    head=pose,
                    antennas=antennas_angles
                )
                time.sleep(dt)
                t += dt  # strict increment

        except KeyboardInterrupt:
            print("!! Interruption detected !!")
            mini.goto_target(
                np.eye(4),
                antennas=[0.0, 0.0], 
                duration=0.5
            )


if __name__ == "__main__":
    main()