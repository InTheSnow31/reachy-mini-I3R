"""
    Training of the policy used in the RLHF training later.
"""

#------------- IMPORTS -------------#

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import torch
import torch.nn as nn
import json
from pathlib import Path
from SoundGenEnv import SoundGenEnv
from pretraining import PretrainPolicy  # pre-trained LSTM 


#------- PATHS AND PARAMETERS -------#

with Path("sound_config.json").open("r", encoding="utf-8") as f:
    content = json.load(f)
    MAX_NOTES = content["MAX_NOTES"]

# Load emotion models
with Path("models/SEVEN_EMOTION_MODEL.json").open("r", encoding="utf-8") as f:
    SEVEN_EMOTION_MODEL = json.load(f)
with Path("models/SIMPLE_BAR_MODEL.json").open("r", encoding="utf-8") as f:
    SIMPLE_BAR_MODEL = json.load(f)
with Path("models/THREE_BAR_MODEL.json").open("r", encoding="utf-8") as f:
    THREE_BAR_MODEL = json.load(f)

INPUTS_FOR_EACH_SESSION = 1
PRETRAINED_PATH = "pretrained_policy.pt"

#------ CUSTOM FEATURE EXTRACTOR ------#

class LSTMFeatureExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space, obs_dim, hidden_dim=128):
        super().__init__(observation_space, features_dim=hidden_dim)
        self.lstm = nn.LSTM(input_size=obs_dim, hidden_size=hidden_dim, batch_first=True)
    
    def forward(self, observations):
        if observations.dim() == 2:
            observations = observations.unsqueeze(1)
        out, (h_n, c_n) = self.lstm(observations)
        return h_n[-1]  


#-------------- TRAINING --------------#

def train(model_name="ppo_note_model"):
    # Vectorized environment
    env = DummyVecEnv([lambda: SoundGenEnv(emotion_model=THREE_BAR_MODEL, max_notes=MAX_NOTES)])
    num_emotions = THREE_BAR_MODEL["number_of_emotions"]
    obs_dim = MAX_NOTES*4 + num_emotions  # Same observation dimension
     
    # Custom feature extractor
    policy_kwargs = dict(
        features_extractor_class=LSTMFeatureExtractor,
        features_extractor_kwargs=dict(obs_dim=obs_dim, hidden_dim=128)
    )

    # Load existing model or create one
    try:
        model = PPO.load(model_name, env=env, policy_kwargs=policy_kwargs)
        print(f"Loading model {model_name}.zip")
    except:
        model = PPO("MlpPolicy", env, verbose=1, n_steps=MAX_NOTES*INPUTS_FOR_EACH_SESSION, policy_kwargs=policy_kwargs)
    
    # Load pre-trained LSTM weights
    if Path(PRETRAINED_PATH).exists():
        pretrained_lstm = PretrainPolicy(obs_dim=obs_dim)
        pretrained_lstm.load_state_dict(torch.load(PRETRAINED_PATH))
        model.policy.features_extractor.lstm.load_state_dict(pretrained_lstm.lstm.state_dict())
        print("Loaded pre-trained LSTM weights into PPO policy")

    # Training loop
    while True:
        print("patate")
        model.learn(total_timesteps=MAX_NOTES * INPUTS_FOR_EACH_SESSION, reset_num_timesteps=False)
        model.save(model_name)
        print("Saved PPO model")


#------------ EXECUTION ------------#

if __name__ == "__main__":
    train()
