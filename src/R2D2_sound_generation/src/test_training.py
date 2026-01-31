#========================================
# Generation from pretrained LSTM policy
#========================================

import torch
import torch.nn.functional as F
from torch.distributions import Categorical
import json
from pathlib import Path

# ---- YOUR IMPORTS ----
from pretraining import PretrainPolicy
from Note import Note
from synthesis.synthesize_whistle_with_harmonics import notes_to_wav


#========================================
# UTILS
#========================================

def sample_categorical(logits, temperature=1.0, deterministic=False):
    """
    Sample or argmax from categorical logits
    """
    if deterministic:
        return torch.argmax(logits)
    probs = F.softmax(logits / temperature, dim=-1)
    return Categorical(probs).sample()


def build_obs_from_actions(actions, emotion, max_notes, device):
    """
    Rebuild observation exactly like during training
    """
    history = torch.zeros(max_notes, 4, device=device)

    if len(actions) > 0:
        recent = torch.stack(actions[-max_notes:])
        history[-len(recent):] = recent[:, :4]

    obs = torch.cat([history.flatten(), emotion])
    return obs.unsqueeze(0).unsqueeze(0)  # (1, 1, obs_dim)


#========================================
# GENERATION FUNCTION
#========================================

def generate_sequence(
    policy,
    emotion,
    max_notes,
    temperature=0.8,
    deterministic=False,
    device="cpu"
):
    """
    Auto-regressive music generation
    """
    policy.eval()
    emotion = torch.tensor(emotion, dtype=torch.float32, device=device)

    actions = []   # raw actions
    notes = []     # Note objects

    for step in range(max_notes):
        obs = build_obs_from_actions(actions, emotion, max_notes, device)
        lengths = torch.tensor([1], device=device)

        with torch.no_grad():
            logits = policy(obs, lengths)

        # ---- decode actions ----
        tone = sample_categorical(logits[0][0, -1], temperature, deterministic)
        duration = sample_categorical(logits[1][0, -1], temperature, deterministic)
        intensity = logits[2][0, -1, 0].clamp(0, 1)
        slide = sample_categorical(logits[3][0, -1], temperature, deterministic)
        end = sample_categorical(logits[4][0, -1], temperature, deterministic)

        action = torch.tensor([
            tone.item(),
            duration.item(),
            intensity.item(),
            slide.item(),
            end.item()
        ], device=device)

        actions.append(action)

        # ---- convert to musical note ----
        pitch = tone.item() + 44
        dur = duration.item() + 1
        note = Note(
            pitch=pitch,
            intensity=float(intensity),
            duration=dur,
            slide=bool(slide.item())
        )
        notes.append(note)

        print(f"[{step}] {note} | end={end.item()}")

        if end.item() == 1:
            break

    return notes


#========================================
# MAIN
#========================================

if __name__ == "__main__":

    DEVICE = "cpu"
    PRETRAINED_PATH = "pretrained_policy.pt"
    OUTPUT_WAV = "generated.wav"

    # ---- Load config ----
    with Path("sound_config.json").open("r", encoding="utf-8") as f:
        cfg = json.load(f)

    MAX_NOTES = cfg["MAX_NOTES"]
    NUM_EMOTIONS = 3
    OBS_DIM = MAX_NOTES * 4 + NUM_EMOTIONS

    # ---- Load model ----
    policy = PretrainPolicy(obs_dim=OBS_DIM)
    policy.load_state_dict(torch.load(PRETRAINED_PATH, map_location=DEVICE))
    policy.to(DEVICE)

    print("✅ Pretrained policy loaded")

    # ---- Choose emotion ----
    emotion = [0, 0, 0] 

    # ---- Generate ----
    notes = generate_sequence(
        policy,
        emotion,
        max_notes=MAX_NOTES,
        temperature=0.8,        # ↑ more creative
        deterministic=False,    # True = always same output
        device=DEVICE
    )

    # ---- Synthesize ----
    print("\n🎵 Synthesizing WAV...")
    notes_to_wav(notes, OUTPUT_WAV)
    print(f"🎧 Audio saved as {OUTPUT_WAV}")
