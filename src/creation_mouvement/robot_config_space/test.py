from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
from reachy_mini.utils.interpolation import InterpolationTechnique

# Limits for the robot space
MAX_ANTENNAS = 3.16
MAX_X_pos = 32
MAX_X_neg = 20
MAX_Y = 60
MAX_Z = 60
MAX_ROLL = 50
MAX_PITCH_pos = 35
MAX_PITCH_neg = 42
MAX_YAW = 90
MAX_BODY_YAW = 21

with ReachyMini() as reachy_mini:
    # Move the head up (10mm on z-axis) and roll it 15 degrees
    pose_0 = create_head_pose()
    pose_1 = create_head_pose(y=20, degrees=True, mm=True)
    pose_2 = create_head_pose(roll=-45, degrees=True, mm=True)
    pose_3 = create_head_pose(x=30, y=10, z=-5, roll=30, pitch=-4, yaw=5, mm=True, degrees=True)

    # Set antennas
    antennas_0 = [0.0, 0.0]
    antennas_1 = [-MAX_ANTENNAS, MAX_ANTENNAS]
    antennas_2 = [MAX_ANTENNAS, -MAX_ANTENNAS]

    # Sequence of poses
    reachy_mini.goto_target(head=pose_1, antennas=antennas_0, duration=1.0, method=InterpolationTechnique.EASE_IN_OUT)

    reachy_mini.goto_target(head=pose_2, antennas=antennas_0, duration=4.0, method=InterpolationTechnique.EASE_IN_OUT)

    reachy_mini.goto_target(head=pose_0, antennas=antennas_0, duration=2.0, body_yaw=0)

    # Reset to default pose
    # pose = create_head_pose() 
    # reachy_mini.goto_target(head=pose, duration=2.0)