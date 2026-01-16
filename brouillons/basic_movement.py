from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

# Connect to the running daemon
with ReachyMini() as mini:
    print("Connected to Reachy Mini! ")
    
    # Wiggle antennas
    print("Wiggling antennas...")
    mini.goto_target(
        head=create_head_pose(),
        duration=1.0
    )
    
    # Look up and tilt head
    mini.goto_target(
        head=create_head_pose(z=20, roll=0, degrees=True, mm=True),
        duration=1.0
    )
    mini.goto_target(
        head=create_head_pose(x=20, z=0, roll=0, degrees=True, mm=True),
        duration=1.0
    )

    mini.goto_target(
        head=create_head_pose(x=0, y=20,roll=0, degrees=True, mm=True),
        duration=1.0
    )

    mini.goto_target(
        head=create_head_pose( roll=20, degrees=True, mm=True),
        duration=1.0
    )
    mini.goto_target(
        head=create_head_pose(roll=0, pitch=20,degrees=True, mm=True),
        duration=1.0
    )

    mini.goto_target(
        head=create_head_pose(pitch=0, yaw=20, degrees=True, mm=True),
        duration=1.0
    )

    mini.goto_target(
        head=create_head_pose(z=-20, yaw=0, degrees=True, mm=True),
        duration=1.0
    )
    mini.goto_target(antennas=[0.5, -0.5], duration=0.5)
    mini.goto_target(antennas=[-0.5, 0.5], duration=0.5)
    mini.goto_target(antennas=[0, 0], duration=0.5)

    print("Done!")