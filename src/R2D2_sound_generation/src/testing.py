#------------- IMPORTS -------------#

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import torch
import torch.nn as nn
import json
from pathlib import Path
from SoundGenEnv import SoundGenEnv
from synthesis.synthesize_whistle_with_harmonics import notes_to_wav
from pretraining import PretrainPolicy  # ton LSTM pré-entraîné
from Note import Note

#------- PATHS AND PARAMETERS -------#

with Path("sound_config.json").open("r", encoding="utf-8") as f:
    content = json.load(f)
    MAX_NOTES = content["MAX_NOTES"]

with Path("models/THREE_BAR_MODEL.json").open("r", encoding="utf-8") as f:
    THREE_BAR_MODEL = json.load(f)


#-------- CLASS AND FUNCTIONS --------#

def test(emotion_vector, model_name="ppo_note_model", output_path = "tests/generation.wav", max_notes=MAX_NOTES, deterministic=False):
    """
    Test a trained PPO model on a single emotion input and generate a sequence of notes.

    Args:
        emotion_vector (list or np.array): List of floats representing the emotion.
        model_name (str): Path to the PPO model to load.
        max_notes (int): Maximum number of notes in the sequence.
        deterministic (bool): If True, use deterministic policy.
    
    Returns:
        actions_list (list): List of generated notes/actions.
    """
    # Reload the environment
    env = DummyVecEnv([lambda: SoundGenEnv(emotion_model=THREE_BAR_MODEL, max_notes=max_notes, evaluation_mode = False)])
    model = PPO.load(model_name, env=env)
    obs = env.reset()
    
    # Inject emotion into obs (depends on your env implementation)
    obs[0, :len(emotion_vector)] = torch.tensor(emotion_vector, dtype=torch.float32)
    
    done = False
    actions_list = []
    
    while not done:
        action, _states = model.predict(obs, deterministic=deterministic)
        obs, reward, done, info = env.step(action)
        actions_list.append(action[0])  # action shape (1, action_dim)
    
    print(actions_list)
    sequence = [Note(n[0], n[1], max(0.20, n[2]), n[3]) for n in actions_list]
    notes_to_wav(sequence, output_path)
    print("Generated sound at : " + output_path)


#------------ EXECUTION ------------#
 
if __name__ == "__main__":
    hapiness = 0 #input("Chose a value for hapiness (0 = Sad, 1 = Happy)")
    explosiveness = 1 #input("Chose a value for explosiveness (0 = Calm, 1 = Explosive)")
    interrogation = 0 #input("Chose a value for Interrogation (0 = Interrogative, 1 = Certain)")
    emotion = [float(hapiness), float(explosiveness), float(interrogation)]
    for i in range(10):
        test(emotion, model_name="ppo_note_model", output_path = "tests/generations/angry_"+str(i)+".wav")