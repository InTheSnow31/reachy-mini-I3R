def choose_motion() -> bool:
    """
    Prompt the user to enable or disable motion.
    
    Returns:
        True  -> motion enabled (YES)
        False -> motion disabled (NO)
    """
    motion_choice = input("Do you want reachy to agree? (YES/NO) [default: YES]: ").strip().upper()
    
    if motion_choice == "" or motion_choice == "YES":
        return True
    else:
        return False

# Example usage in main
if __name__ == "__main__":
    motion_enabled = choose_motion()
    if motion_enabled:
        print("Motion enabled.")
    else:
        print("Motion disabled.")