def get_duration(default: float = 10.0) -> float:
    """
    Ask the user for the movement duration in seconds.
    Press Enter to use the default value.
    """
    try:
        user_input = input(f"Movement duration in seconds (default {default}): ")
        
        if user_input.strip() == "":
            return default
        
        duration = float(user_input)
        
        if duration <= 0:
            print("Invalid duration → using default value.")
            return default
        
        return duration

    except ValueError:
        print("Invalid input → using default value.")
        return default