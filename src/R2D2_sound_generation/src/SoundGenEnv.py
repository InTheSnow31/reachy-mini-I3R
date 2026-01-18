
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
from Emotion import random_emotion
import json

#------ CLASSES AND FUNCTIONS ------#

class SoundGenEnv(gym.Env):
    def __init__(self, emotion_model, max_notes=16, evaluation_mode = True):
        self.evaluation_mode = evaluation_mode
        self.EMOTION_MODEL = emotion_model
        with Path("sound_config.json").open("r", encoding="utf-8") as f:
            super().__init__()
            json_content = json.load(f)
            self.max_notes = json_content["MAX_NOTES"]
            self.current_step = 0
            self.notes = []
            self.note_range = json_content["TONES_RANGE"]
            self.num_intensity_bins = 10  # Intensity levels 
            self.duration_range = json_content["DURATION_SCALE"]  # Note Duration

        self.action_space = spaces.MultiDiscrete([self.note_range, self.duration_range, self.num_intensity_bins, 2, 2]) # Notes, Duratio, Intensity, Slide ?, Final Note ?

        obs_dim = self.max_notes*4 + self.EMOTION_MODEL["number_of_emotions"]
        self.observation_space = spaces.Box(low=0, high=1, shape=(obs_dim,), dtype=np.float32)


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
            print("Reward ", reward)
        
        else :
            emotion_generated = [0, 0, 0]
            reward = 0
        
        return reward


    def step(self, action):
        pitch = action[0] + 44
        duration = action[1] + 1
        intensity = (action[2]+1) / (self.num_intensity_bins)
        slide = action[3]
        end = action[4]
        note = Note(pitch, intensity, duration, slide == 1)
        self.notes.append(note)
        self.current_step += 1

        #Ending generation condition
        done = self.current_step >= self.max_notes or end == 1

        reward = 0
        if done:
            reward = self.evaluate_sequence(self.notes)

        obs = self._get_obs()
        info = {"note": note, "sequence": self.notes.copy(), "target_emotion": self.target_emotion}
        return obs, reward, done, info

