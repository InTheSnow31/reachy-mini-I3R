from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import torch
import torch.nn as nn
import json
from pathlib import Path
from SoundGenEnv import SoundGenEnv
from pretraining import PretrainPolicy  # ton LSTM pré-entraîné

with Path("sound_config.json").open("r", encoding="utf-8") as f:
    content = json.load(f)
    MAX_NOTES = content["MAX_NOTES"]

###### PARAMETERS ######

INPUTS_PAR_SESSIONS = 5
PRETRAINED_PATH = "pretrained_policy.pt"

# Load emotion models
with Path("models/SEVEN_EMOTION_MODEL.json").open("r", encoding="utf-8") as f:
    SEVEN_EMOTION_MODEL = json.load(f)
with Path("models/SIMPLE_BAR_MODEL.json").open("r", encoding="utf-8") as f:
    SIMPLE_BAR_MODEL = json.load(f)
with Path("models/THREE_BAR_MODEL.json").open("r", encoding="utf-8") as f:
    THREE_BAR_MODEL = json.load(f)

###### CUSTOM FEATURE EXTRACTOR ######

class LSTMFeatureExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space, obs_dim, hidden_dim=128):
        super().__init__(observation_space, features_dim=hidden_dim)
        # Reuse your pre-trained LSTM
        self.lstm = nn.LSTM(input_size=obs_dim, hidden_size=hidden_dim, batch_first=True)
    
    def forward(self, observations):
        if observations.dim() == 2:
            observations = observations.unsqueeze(1)
        out, (h_n, c_n) = self.lstm(observations)
        return h_n[-1]  # dernier hidden state

###### TRAINING ######

def train(model_name="ppo_note_model"):
    # Vectorized environment
    env = DummyVecEnv([lambda: SoundGenEnv(emotion_model=THREE_BAR_MODEL, max_notes=MAX_NOTES)])

    # Observation dimension
    num_emotions = THREE_BAR_MODEL["number_of_emotions"]
    obs_dim = MAX_NOTES*4 + num_emotions  # same as pretrain
     
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
        model = PPO("MlpPolicy", env, verbose=1, n_steps=MAX_NOTES*INPUTS_PAR_SESSIONS, policy_kwargs=policy_kwargs)
    
    # Load pre-trained LSTM weights
    if Path(PRETRAINED_PATH).exists():
        pretrained_lstm = PretrainPolicy(obs_dim=obs_dim)
        pretrained_lstm.load_state_dict(torch.load(PRETRAINED_PATH))
        model.policy.features_extractor.lstm.load_state_dict(pretrained_lstm.lstm.state_dict())
        print("Loaded pre-trained LSTM weights into PPO policy")

    # Training loop
    while True:
        model.learn(total_timesteps=1, reset_num_timesteps=False)
        model.save(model_name)
        print("Saved PPO model")

###### TESTING ######

def test(emotion_vector, model_name="ppo_note_model", max_notes=16, deterministic=False):
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
    # Create the environment
    env = DummyVecEnv([lambda: SoundGenEnv(emotion_model={"number_of_emotions": len(emotion_vector)},
                                           max_notes=max_notes)])
    
    # Load PPO model
    model = PPO.load(model_name, env=env)
    
    # Reset environment with the emotion
    obs = env.reset()
    
    # Inject emotion into obs (depends on your env implementation)
    # Here we assume the env uses the first part of obs for emotion
    obs[0, :len(emotion_vector)] = torch.tensor(emotion_vector, dtype=torch.float32)
    
    done = False
    actions_list = []
    
    while not done:
        action, _states = model.predict(obs, deterministic=deterministic)
        obs, reward, done, info = env.step(action)
        actions_list.append(action[0])  # action shape (1, action_dim)
    
    return actions_list

###### MAIN ######

if __name__ == "__main__":
    train()
    # Exemple d’émotion
    #emotion = [0.8, 0.1, 0.5]  # par exemple Valence, Arousal, Energy

    # Générer la séquence de notes
    #sequence = test(emotion, model_name="ppo_note_model")

    #print("Generated sequence:", sequence)
