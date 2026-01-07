from stable_baselines3 import PPO
from stable_baselines3.common.env_util import DummyVecEnv
from SoundGenEnv import SoundGenEnv

###### PARAMETERS ######

MAX_NOTES = 8
INPUTS_PAR_SESSIONS = 5 

########################

# Wrapper pour SB3 (obligatoire pour vectorized env)
env = DummyVecEnv([lambda: SoundGenEnv(max_notes=8)])

# Créer l'agent PPO
try :
    model = PPO.load("ppo_note_model", env=env)
    print("Modèle chargé depuis ppo_note_model.zip")
except :
    model = PPO("MlpPolicy", env, verbose=1)

while True:
    model.learn(total_timesteps= MAX_NOTES * INPUTS_PAR_SESSIONS, reset_num_timesteps=False)
    model.save("ppo_note_model")

# Sauvegarder

# Reprendre plus tard

"""model = PPO.load("ppo_note_model", env=env)

obs = env.reset()
done = False
while not done:
    action, _states = model.predict(obs, deterministic=False)
    obs, reward, done, info = env.step(action)
    print(info[0]["note"])  # info est une liste car DummyVecEnv"""
