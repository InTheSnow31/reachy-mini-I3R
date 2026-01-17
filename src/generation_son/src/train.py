from stable_baselines3 import PPO
from stable_baselines3.common.env_util import DummyVecEnv
from SoundGenEnv import SoundGenEnv
import json
from pathlib import Path

###### PARAMETERS ######

MAX_NOTES = 4
INPUTS_PAR_SESSIONS = 5

with Path("models\SEVEN_EMOTION_MODEL.json").open("r", encoding="utf-8") as f:
    SEVEN_EMOTION_MODEL = json.load(f)

with Path("models\SIMPLE_BAR_MODEL.json").open("r", encoding="utf-8") as f:
    SIMPLE_BAR_MODEL = json.load(f)

with Path("models\THREE_BAR_MODEL.json").open("r", encoding="utf-8") as f:
    THREE_BAR_MODEL = json.load(f)


###### TRAINING AND TESTING ######

def train(model_name="ppo_note_model"):
    # Wrapper for vectorized environment
    env = DummyVecEnv([lambda: SoundGenEnv(emotion_model = SIMPLE_BAR_MODEL, max_notes=MAX_NOTES)])

    # Load existing model or create one
    try :
        model = PPO.load(model_name, env=env)
        print(f"Loading model {model_name}.zip")
    except :
        model = PPO("MlpPolicy", env, verbose=1, n_steps=MAX_NOTES*INPUTS_PAR_SESSIONS)

    while True:
        model.learn(total_timesteps= 1, reset_num_timesteps=False)
        model.save(model_name)
        print("Saved")


def test(model_name="ppo_note_model"):
    env = DummyVecEnv([lambda: SoundGenEnv(emotion_model = THREE_BAR_MODEL, max_notes=MAX_NOTES)])
    model = PPO.load(model_name, env=env)
    print(f"Loaded model {model_name}.zip")
    obs = env.reset()
    done = False
    # Generating notes till done
    while not done:
        action, _states = model.predict(obs, deterministic=False)
        obs, reward, done, info = env.step(action)
        print(info[0]["note"])


###### MAIN ######

if __name__ == "__main__":
    train()
    #test()
