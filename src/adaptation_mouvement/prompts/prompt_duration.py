def get_duration(default: float = 10.0) -> float:
    """
    Demande à l'utilisateur la durée du mouvement.
    Appuyer sur Entrée → durée par défaut.
    """
    try:
        user_input = input(f"Durée du mouvement en secondes (défaut {default}) : ")
        
        if user_input.strip() == "":
            return default
        
        duration = float(user_input)
        
        if duration <= 0:
            print("Durée invalide → utilisation de la valeur par défaut.")
            return default
        
        return duration

    except ValueError:
        print("Entrée invalide → utilisation de la valeur par défaut.")
        return default