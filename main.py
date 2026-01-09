from stable_baselines3 import PPO
from stable_baselines3.common.env_util import DummyVecEnv
from SoundGenEnv import SoundGenEnv

###### PARAMETERS ######

MAX_NOTES = 4
INPUTS_PAR_SESSIONS = 5

SEVEN_EMOTION_MODEL = {
    "system" : "wheel",
    "wheel_path" : "models/7_emotions_wheel.png",
    "number_of_emotions" : 7,
    "emotion_names" : ['happiness', 'sadness', 'anger', 'fear', 'love','disgust','surprise'],
    "wheel_offset" : -90
}

SIMPLE_BAR_MODEL = {
    "system" : "bars",
    "number_of_emotions" : 2,
    "emotion_names" : [('Negatvie', 'Positive'), ('Calme','Surpris')]
}

########################

# Wrapper pour SB3 (obligatoire pour vectorized env)
env = DummyVecEnv([lambda: SoundGenEnv(emotion_model = SIMPLE_BAR_MODEL, max_notes=MAX_NOTES)])

# Créer l'agent PPO
try :
    model = PPO.load("ppo_note_model", env=env)
    print("Modèle chargé depuis ppo_note_model.zip")
except :
    model = PPO("MlpPolicy", env, verbose=1, n_steps=MAX_NOTES*INPUTS_PAR_SESSIONS)

while True:
    model.learn(total_timesteps= 1, reset_num_timesteps=False)
    model.save("ppo_note_model")
    print("Saved")

# Sauvegarder

# Reprendre plus tard

"""model = PPO.load("ppo_note_model", env=env)

obs = env.reset()
done = False
while not done:
    action, _states = model.predict(obs, deterministic=False)
    obs, reward, done, info = env.step(action)
    print(info[0]["note"])  # info est une liste car DummyVecEnv"""
