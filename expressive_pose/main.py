from robot_config_space.pose_generation import generate_pose_from_pad
import json
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

def main():

    print("Hello! Try different emotions here.\nType 'q' and enter if you want to quit.")

    while True:

        # 1. Choix de l’émotion
        emotion = input("\nWhich emotion would you like to try? ").strip().lower()
        if emotion == "q":
            print("\nQuitting.\n")
            break

        duration_min = float(input("Indicate a minimal duration (seconds): "))

        # 2. Charger PAD
        with open("emotional_space/pad.json") as f:
            pad_data = json.load(f)

        if emotion not in pad_data["emotions"]:
            print(f"\nEmotion '{emotion}' unknown.")
            return

        P = pad_data["emotions"][emotion]["P"]
        A = pad_data["emotions"][emotion]["A"]
        D = pad_data["emotions"][emotion]["D"]

        # 3. Générer la pose depuis PAD
        pose = generate_pose_from_pad(P, A, D)
        print(f"\nGenerated pose for {emotion}: {pose}")

        # 4. Exécution sur Reachy
        with ReachyMini() as reachy:
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
                body_yaw=pose["body_yaw"],
                antennas=pose["antennas"],
                duration=duration_min,
            )


if __name__ == "__main__":
    main()
