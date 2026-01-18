from movement_sound_generation import generate
from adapted_motion import adapt
# from sound_generation import train

def main():
    """
    Entry point of the program.

    Prompts the user to select an execution mode and dispatches
    the corresponding module.
    """

    # Ask user which mode to launch
    mode: int = int(
        input(
            "\n\nHello! Which mode do you want to launch? Just type 1, 2, or 3.\n\n"
            "1 = Movement adaptation\n"
            "2 = Movement generation with sound\n"
            "3 = AI training for sound\n\n"
            "Your choice: "
        )
    )

    print(f"Launching module: {mode}\n")

    # Dispatch according to selected mode
    if mode == 1:
        adapt.main()

    elif mode == 2:
        generate.main()

    elif mode == 3:
        print("Go to R2D2_sound_generation/src/ and lunch the 'testing.py' script.")
        # train.train()

    else:
        # Safety fallback for invalid input
        print("Invalid mode selected. Exiting.")


if __name__ == "__main__":
    main()