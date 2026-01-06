from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
from robot-config-space.pose-generation import sample_pose

DURATION = 1.5

def main():
    pose = sample_pose()
    print("Generated pose:", pose)

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
            duration=DURATION,
        )

if __name__ == "__main__":
    main()
