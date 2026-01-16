"""Reachy Mini example that plays yes/no motions driven by a sine wave."""

import time
from typing import Literal

import numpy as np
from scipy.spatial.transform import Rotation as R

from reachy_mini import ReachyMini


def prompt_float(prompt: str, default: float) -> float:
    """Ask the user for a float while supporting defaults."""
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if not raw:
            return default
        try:
            return float(raw)
        except ValueError:
            print("Please enter a numeric value.")


def prompt_motion_type() -> Literal["yes", "no"]:
    """Ask the user which motion to play."""
    while True:
        motion = input("Motion to play (yes/no) [yes]: ").strip().lower()
        if motion in {"", "yes"}:
            return "yes"
        if motion == "no":
            return "no"
        print("Please answer with 'yes' or 'no'.")


def main() -> None:
    print("Configure an emotive yes/no motion (values in radians and Hertz).")
    motion_type = prompt_motion_type()
    amplitude = prompt_float("Amplitude", 0.35)
    frequency = prompt_float("Frequency", 0.6)

    print(
        f"Playing a '{motion_type}' motion with amplitude={amplitude} rad "
        f"and frequency={frequency} Hz. Press Ctrl+C to stop."
    )

    with ReachyMini(media_backend="no_media") as reachy_mini:
        reachy_mini.goto_target(np.eye(4), antennas=[0.0, 0.0], duration=1.0)
        pose = np.eye(4)
        base_antennas = [0.0, 0.0]

        try:
            t0 = time.time()
            while True:
                t = time.time() - t0
                angle = amplitude * np.sin(2 * np.pi * frequency * t)
                if motion_type == "yes":
                    euler_rot = np.array([0.0, angle, 0.0])  # pitch only
                else:
                    euler_rot = np.array([0.0, 0.0, angle])  # yaw only

                pose[:3, :3] = R.from_euler("xyz", euler_rot, degrees=False).as_matrix()
                reachy_mini.set_target(head=pose, antennas=base_antennas)
                time.sleep(0.01)
        except KeyboardInterrupt:
            print("\nStopping motion and returning to neutral pose.")
            reachy_mini.goto_target(np.eye(4), antennas=base_antennas, duration=1.0)


if __name__ == "__main__":
    main()
