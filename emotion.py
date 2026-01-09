import math
import random

class emotion:
    def __init__(self, emotion_list):
        self.emotion_list = emotion_list

    def l(self):
        return self.emotion_list

def random_emotion(EMOTION_MODEL):
    if EMOTION_MODEL["system"] == "wheels" :
        r = random.random()
        theta = random.random() * 2*math.pi
        return polar_to_emotion(EMOTION_MODEL, r, theta)
    elif EMOTION_MODEL["system"] == "bars" :
        emotions = []
        for bar in EMOTION_MODEL["emotion_names"]:
            val = random.randint(0,5)
            emotions.append(val)
        return emotion(emotions)

def polar_to_emotion(EMOTION_MODEL, r, theta):
    # r = 0 à 1
    echelle = 5
    theta_offset = math.radians(EMOTION_MODEL["wheel_offset"]) #Initialement Anger à 0 rad
    theta = (theta + theta_offset) % (2*math.pi)
    emotions = EMOTION_MODEL["emotion_names"]
    emotions = [0]*len(emotions)
    angle_per_emotion = 2 * math.pi / len(emotions)
    theta_in_cadrant = theta % angle_per_emotion
    pourcentage_in_cadrant = theta_in_cadrant / angle_per_emotion
    indice_cadrant = int(theta // angle_per_emotion)
    emotions[indice_cadrant] = round((1-pourcentage_in_cadrant) * r * echelle)
    emotions[(indice_cadrant+1) % len(emotions)] = round(pourcentage_in_cadrant * r * echelle)
    return emotion(emotions)

#print(polar_to_emotion(1, math.radians(-90)))
#print(random_emotion())