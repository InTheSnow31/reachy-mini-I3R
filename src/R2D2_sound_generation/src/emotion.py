import math
import random

def random_emotion(EMOTION_MODEL):
    if EMOTION_MODEL["system"] == "wheels" :
        r = random.random()
        theta = random.random() * 2*math.pi
        return polar_to_emotion(EMOTION_MODEL, r, theta)
    
    elif EMOTION_MODEL["system"] == "bars" :
        return [random.random() for e in EMOTION_MODEL["emotion_names"]]

def polar_to_emotion(EMOTION_MODEL, r, theta):

    # Ajusted angle with offset
    theta = (theta + math.radians(EMOTION_MODEL["wheel_offset"])) % (2*math.pi) 

    #Position of theta in the wheel
    angle_per_emotion = 2 * math.pi / EMOTION_MODEL["number_of_emotions"]
    theta_in_cadrant = theta % angle_per_emotion
    pourcentage_in_cadrant = theta_in_cadrant / angle_per_emotion
    indice_cadrant = int(theta // angle_per_emotion)

    # Emotion vector
    emotions = [0]*EMOTION_MODEL["number_of_emotions"]
    emotions[indice_cadrant] = (1-pourcentage_in_cadrant) * r
    emotions[(indice_cadrant+1) % len(emotions)] = pourcentage_in_cadrant * r

    return emotions

#print(polar_to_emotion(1, math.radians(-90)))
#print(random_emotion())