from creation_mouvement import generate
# from adaptation_mouvement import adapt
# from generation_son import train 

def main():
    mode = int(input("\n\nBonjour ! Quel mode voulez-vous lancer ? Tapez juste 1, 2 ou 3.\n\n1 = Adaptation d'un mouvement\n2 = Génération d'un mouvement avec son\n3 = Entraînement de l'IA pour le son\n\nVotre choix : "))

    print(f"Lancement du module : {mode}")

    if mode == 1:
        print("Mode non implémenté pour l'instant.")
        # adapt.main()
    elif mode == 2:
        generate.main()
    elif mode == 3:
        print("Mode d'entraînement non implémenté pour l'instant.")
        # train.train()

if __name__ == "__main__":
    main()