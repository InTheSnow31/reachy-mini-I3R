import math
import random

class emotion:
    def __init__(self, happiness, sadness, anger, fear, love, disgust, surprise):
        self.love = love
        self.fear = fear
        self.anger = anger
        self.sadness = sadness
        self.happiness = happiness
        self.disgust = disgust
        self.surprise = surprise

    def l(self):
        return [self.happiness, self.sadness, self.anger, self.fear, self.love, self.disgust, self.surprise]

def random_emotion():
    r = random.random()
    theta = random.random() * 2*math.pi
    return polar_to_emotion(r, theta)

def polar_to_emotion(r, theta):
    # r = 0 à 1
    echelle = 5
    theta_offset = math.radians(90) #Initialement Anger à 0 rad
    theta = (theta + theta_offset) % (2*math.pi)
    emotions = ['happiness', 'sadness', 'anger', 'fear', 'love','disgust','surprise']
    emotions = [0]*len(emotions)
    angle_per_emotion = 2 * math.pi / len(emotions)
    theta_in_cadrant = theta % angle_per_emotion
    pourcentage_in_cadrant = theta_in_cadrant / angle_per_emotion
    indice_cadrant = int(theta // angle_per_emotion)
    emotions[indice_cadrant] = round((1-pourcentage_in_cadrant) * r * echelle)
    emotions[(indice_cadrant+1) % len(emotions)] = round(pourcentage_in_cadrant * r * echelle)
    return emotion(happiness=emotions[0], sadness=emotions[1], anger=emotions[2], fear=emotions[3], love=emotions[4], disgust=emotions[5], surprise=emotions[6])

#print(polar_to_emotion(1, math.radians(-90)))
#print(random_emotion())