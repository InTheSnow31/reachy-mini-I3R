
#------------- IMPORTS -------------#

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import gym
from gym import spaces
import numpy as np
from synthesis.synthesize_whistle_with_harmonics import notes_to_wav
from Note import Note
from RLHF_interface import input
from emotion import random_emotion
import json

#------ CLASSES AND FUNCTIONS ------#

class SoundGenEnv(gym.Env):
    def __init__(self, emotion_model, max_notes=16, evaluation_mode=True):
        super().__init__()  # toujours en premier
        self.evaluation_mode = evaluation_mode
        self.EMOTION_MODEL = emotion_model
        self.max_notes = max_notes
        self.current_step = 0
        self.notes = []

        # Charger config
        with open("sound_config.json", "r", encoding="utf-8") as f:
            cfg = json.load(f)
            self.note_range = cfg["TONES_RANGE"]
            self.duration_range = cfg["DURATION_SCALE"]

        # Action : MultiDiscrete pour les discrets, Box pour intensity
        self.action_space_discrete = gym.spaces.MultiDiscrete([
            self.note_range,  # tone
            self.duration_range,  # duration
            2,  # sliding
            2   # final
        ])
        self.action_space_continuous = gym.spaces.Box(
            low=0.0, high=1.0, shape=(1,), dtype=np.float32
        )

        # Pour SB3, tu peux concaténer en un seul Box si tu veux
        self.action_space = gym.spaces.Box(
            low=np.array([0,0,0,0,0], dtype=np.float32),
            high=np.array([self.note_range-1, self.duration_range-1, 1, 1, 1], dtype=np.float32),
            dtype=np.float32
        )

        # Observation
        obs_dim = self.max_notes*4 + self.EMOTION_MODEL["number_of_emotions"]
        self.observation_space = gym.spaces.Box(low=0.0, high=1.0, shape=(obs_dim,), dtype=np.float32)


    def reset(self):
        self.notes = []
        self.current_step = 0
        self.target_emotion = random_emotion(self.EMOTION_MODEL)
        return self._get_obs()


    def _get_obs(self):
        # Notes already generated
        obs_notes = np.zeros((self.max_notes,4), dtype=np.float32)
        for i, note in enumerate(self.notes):
            obs_notes[i,0] = note.pitch / 24
            obs_notes[i,1] = note.intensity
            obs_notes[i,2] = (note.duration-1)/3
            obs_notes[i,3] = 1 if note.slide else 0
        obs_notes = obs_notes.flatten()  # size = max_notes*3
        return np.concatenate([obs_notes, self.target_emotion]) 


    def estimate_emotion(self, notes):
        notes_to_wav(notes, "temp/temp.wav")
        interface = input(self.EMOTION_MODEL)
        return interface.loop()


    def evaluate_sequence(self, notes):
        if self.evaluation_mode :
            emotion_generated = self.estimate_emotion(notes)
        
            reward = -np.linalg.norm(np.array(emotion_generated) - np.array(self.target_emotion))

            print("#################################")
            print("Targeted emotion :", self.target_emotion)
            print("Evaluated emotion :", emotion_generated)
            print("Notes :")
            for n in notes :
                print("**", n)
            print("Reward ", reward)
        
        else :
            emotion_generated = [0, 0, 0]
            reward = 0
        
        return reward


    def step(self, action):
        # action[0:4] = tone, duration, sliding, final
        # action[4] = intensity
        tone = int(action[0])
        duration = int(action[1])
        slide = int(action[2]) == 1
        end = int(action[3]) == 1
        intensity = float(action[4])  # continu

        pitch = tone + 44
        duration = duration + 1
        note = Note(pitch, intensity, duration, slide)
        self.notes.append(note)
        self.current_step += 1

        done = self.current_step >= self.max_notes or end
        reward = self.evaluate_sequence(self.notes) if done else 0

        obs = self._get_obs()
        info = {"note": note, "sequence": self.notes.copy()}
        return obs, reward, done, info

