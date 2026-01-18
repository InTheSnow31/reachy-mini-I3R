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


# with ReachyMini(media_backend="no_media") as reachy_mini:
#     reachy_mini.goto_target(
#             create_head_pose(x=0, y=0,z=30, roll=0, pitch=0,yaw=-40, degrees=True, mm=True), 
#             antennas=[0.0, 0.0], 
#             duration=1.0)