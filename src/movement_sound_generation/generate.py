from typing import Dict, Any

import json
import os

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

from movement_sound_generation.robot_config_space.pose_generation import generate_pose
from movement_sound_generation.sound.sound_generation import generate_sound
from movement_sound_generation.emotional_space import convert


def normalize_pad_json(data: dict) -> dict:
    """
    Converts PAD values from [-1; 1] to [0; 1].
    Returns a dictionnary of PAD values for each emotion.
    """
    def norm(x: float) -> float:
        return max(0.0, min(1.0, (x + 1.0) * 0.5))

    for emo in data.get("emotions", {}).values():
        for k in ("P", "A", "D"):
            if k in emo:
                emo[k] = norm(emo[k])
    return data


def main() -> None:
    """
    Interactive loop to test emotional behaviors on Reachy Mini.

    The user selects an emotion, which is mapped to PAD (Pleasure, Arousal,
    Dominance) values. Based on this emotional state, the system repeatedly:
    - Generates a robot pose
    - Synthesizes a sound matching the emotion
    - Executes both synchronously on the robot

    The loop continues until the minimum requested duration is reached
    or the user quits.
    """

    # Initialize Reachy Mini context
    with ReachyMini() as reachy:

        print("\nHello! Try different emotions here.")
        print("Type 'q' and press enter if you want to quit.\n")

        while True:

            # --- 1. Emotional state selection ---
            emotion: str = input(
                "\nWhich emotion would you like to try? "
            ).strip().lower()

            if emotion == "q":
                print("\nQuitting.\n")
                break

            duration_min: float = float(
                input("Indicate a minimum duration (seconds): ")
            )

            # --- 2. Load PAD emotional space ---
            current_dir: str = os.path.dirname(os.path.abspath(__file__))
            json_path: str = os.path.join(
                current_dir, "emotional_space", "pad.json"
            )

            with open(json_path, "r", encoding="utf-8") as f:
                pad_data = json.load(f)

            pad_data = normalize_pad_json(pad_data)

            P: float = pad_data["emotions"][emotion]["P"]
            A: float = pad_data["emotions"][emotion]["A"]
            D: float = pad_data["emotions"][emotion]["D"]

            # --- 3. Prepare execution ---
            duration: float = 0.0
            reachy.media.start_playing()

            # --- 4. Generate and execute until minimum duration is reached ---
            while duration <= duration_min:

                # Generate pose parameters from emotional state
                pose: Dict[str, Any] = generate_pose(P, A, D)
                print(f"\nGenerated pose for '{emotion}': {pose}")

                # Generate corresponding emotional sound
                sound = generate_sound(P, A, D, pose["duration"])

                # Push audio to Reachy Mini buffer
                reachy.media.push_audio_sample(sound)

                duration += pose["duration"]

                # --- 5. Build and execute robot motion ---
                head = create_head_pose(
                    x=pose["x"],
                    y=pose["y"],
                    z=pose["z"],
                    roll=pose["roll"],
                    pitch=pose["pitch"],
                    yaw=pose["yaw"],
                    mm=True,
                    degrees=True,
                )

                reachy.goto_target(
                    head=head,
                    antennas=pose["antennas"],
                    duration=pose["duration"],
                    method=pose["method"],
                    body_yaw=pose["body_yaw"],
                )

                print("Body yaw:", pose["body_yaw"])


if __name__ == "__main__":
    main()
