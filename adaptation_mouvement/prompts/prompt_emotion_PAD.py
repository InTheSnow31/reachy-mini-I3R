# Quelques émotions avec les valeurs calculées par Mehrabian et Russell
# Valence, Arousal, Dominance
EMOTION_PAD = {
    "joy":        ( 0.76,  0.48,  0.35),
    "sadness":    (-0.63, 0.27, -0.33),
    "anger":      (-0.43,  0.67,  -0.13),
    "fear":       (-0.64,  0.6, -0.43),
    "disgust":    (-0.6,  0.35,  0.11),
    "surprise":   ( 0.4,  0.67,  -0.13),
    #"scornfulness": (-0.5,  0.35,  -0.2),
    #"relaxed":    ( 0.5, -0.2,  0.3),
    #"mildness":   ( 0.2, -0.1,  0.1),
}

def get_emotion_PAD() -> tuple[float, float, float]:
    """
    Ask the user if they want to select PAD values manually or pick an emotion.
    Returns (pleasure, arousal, dominance).
    """
    use_manual = input("Do you want to choose PAD values manually? (yes/no) [no]: ").strip().lower() or "no"

    if use_manual in ["yes", "y"]:
        # Manuel
        while True:
            try:
                pleasure = float(input("Pleasure (-1 to 1) [0.0]: ") or 0.0)
                arousal  = float(input("Arousal  (-1 to 1) [0.0]: ") or 0.0)
                dominance= float(input("Dominance (-1 to 1) [0.0]: ") or 0.0)

                # Clamp
                pleasure  = max(-1, min(1, pleasure))
                arousal   = max(-1, min(1, arousal))
                dominance = max(-1, min(1, dominance))

                print(f"Selected PAD values: Pleasure={pleasure}, Arousal={arousal}, Dominance={dominance}")
                return pleasure, arousal, dominance

            except ValueError:
                print("Please enter numeric values between -1 and 1.")

    else:
        # Choix par émotions
        print("Pick an emotion by pressing Enter. The associated PAD values will be selected:")

        emotions = list(EMOTION_PAD.keys())
        for i, emotion in enumerate(emotions, 1):
            print(f"{i}. {emotion.capitalize()}")

        while True:
            choice = input("Your choice (number or Enter to select default emotion): ").strip()

            if choice == "":
                # Si utilisateur ne tape rien, prend la première émotion
                emotion = emotions[0]
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(emotions):
                emotion = emotions[int(choice)-1]
                break
            else:
                print("Invalid input. Choose a number from the list or press Enter.")

        pad = EMOTION_PAD[emotion]
        print(f"Selected emotion: {emotion.capitalize()} -> PAD values: Pleasure={pad[0]}, Arousal={pad[1]}, Dominance={pad[2]}")
        return pad