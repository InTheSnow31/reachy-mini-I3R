from robot_config_space.pose_generation import generate_pose
from sound.sound_generation import generate_sound
import json
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

def main():

    with ReachyMini() as reachy:

        print("Hello! Try different emotions here.\nType 'q' and enter if you want to quit.")

        while True:

            # 1. Emotionnal state choice
            emotion = input("\nWhich emotion would you like to try? ").strip().lower()
            if emotion == "q":
                print("\nQuitting.\n")
                break

            duration_min = float(input("Indicate a minimum duration (seconds): "))

            # 2. PAD loading
            with open("emotional_space/pad.json") as f:
                pad_data = json.load(f)

            if emotion not in pad_data["emotions"]:
                print(f"\nEmotion '{emotion}' unknown.")
                return

            P = pad_data["emotions"][emotion]["P"]
            A = pad_data["emotions"][emotion]["A"]
            D = pad_data["emotions"][emotion]["D"]

            # 3. Pose and sound preparation
            duration = 0
            reachy.media.start_playing()

            while (duration <= duration_min):

                # 4. Pose and sound generation
                pose = generate_pose(P, A, D)
                print(f"\nGenerated pose for {emotion}: {pose}")
                sound = generate_sound(P, A, D, pose["duration"])

                reachy.media.push_audio_sample(sound)

                duration+=pose["duration"]

                # 5. Execution
                
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
                    body_yaw=pose["body_yaw"]
                )

                print("The body yaw is of:" + str(pose["body_yaw"]))


if __name__ == "__main__":
    main()
