#------------- IMPORTS -------------#

import torch
from torch import nn, optim
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence, pad_packed_sequence
from torch.utils.data import Dataset, DataLoader, random_split
from pathlib import Path
import matplotlib.pyplot as plt
import json
import numpy as np


#--------- PYTORCH DATASET ---------#

class SoundSeqDataset(Dataset):
    def __init__(self, dataset_folder):
        self.files = sorted(Path(dataset_folder).glob("*.pt"))

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        data = torch.load(self.files[idx])
        return data["emotion"], data["actions"]  # actions: (T, 5)


def collate_fn(batch):
    emotions = []
    actions = []
    lengths = []

    for e, a in batch:
        emotions.append(e)
        actions.append(a)
        lengths.append(len(a))

    actions_padded = pad_sequence(actions, batch_first=True, padding_value=0)
    emotions = torch.stack(emotions)
    lengths = torch.tensor(lengths)
    return emotions, actions_padded, lengths


#------------ LSTM MODEL ------------#

class PretrainPolicy(nn.Module):
    def __init__(self, obs_dim, hidden_dim=128, num_layers=1):
        with Path("sound_config.json").open("r", encoding="utf-8") as f:
            json_content = json.load(f)
            action_dims = [
                json_content["TONES_RANGE"],
                json_content["DURATION_SCALE"],
                1,
                2,
                2
            ]
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=obs_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True
        )
        #self.heads = nn.ModuleList([nn.Linear(hidden_dim, dim) for dim in action_dims])
        self.heads = nn.ModuleList([
            nn.Linear(hidden_dim, action_dims[0]),  # Tone
            nn.Linear(hidden_dim, action_dims[1]),  # Duration
            nn.Sequential(                          # Intensity ∈ [0,1]
                nn.Linear(hidden_dim, 1),
                nn.Sigmoid()
            ),
            nn.Linear(hidden_dim, 2),               # Flag1
            nn.Linear(hidden_dim, 2),               # Flag2
        ])

    def forward(self, x, lengths):
        packed = pack_padded_sequence(x, lengths.cpu(), batch_first=True, enforce_sorted=False)
        packed_out, _ = self.lstm(packed)
        out, _ = pad_packed_sequence(packed_out, batch_first=True)
        logits = [head(out) for head in self.heads]  # list de (B, T, dim_i)
        return logits


#------------ LOSS UTILS ------------#

def compute_losses(logits, actions, lengths, ce_losses):
    """
    Calcule la loss moyenne par dimension et la loss totale = somme des 5 dimensions.
    Le padding est ignoré.
    """
    B, T, _ = actions.shape
    device = actions.device
    num_dims = len(logits)

    mask = torch.arange(T, device=device)[None, :] < lengths[:, None]
    mask_flat = mask.view(-1)

    losses_per_dim = []

    loss_weights = torch.tensor(
        [0.5, 1.0, 3.0, 2.0, 4.0], device=device
    )

    for i in range(num_dims):
        logit = logits[i]                    # (B, T, K)
        target = actions[:, :, i].float() if i == 2 else actions[:, :, i]

        logit_flat = logit.view(-1, logit.size(-1))[mask_flat]

        if i == 2:  # Intensity ∈ [0,1]
            target_flat = target.view(-1, 1)[mask_flat]
        else:
            target_flat = target.view(-1)[mask_flat]

        loss_i = ce_losses[i](logit_flat, target_flat)  # moyenne
        loss_i = loss_i * loss_weights[i]
        losses_per_dim.append(loss_i)

    total_loss = torch.stack(losses_per_dim).sum()
    return losses_per_dim, total_loss


def build_obs(emotions, actions, max_notes):
    """
    Construit les observations pour LSTM à partir de l'historique et des émotions.
    """
    B, T, _ = actions.shape
    obs_list = []

    for b in range(B):
        history = torch.zeros(max_notes, 4)
        seq_obs = []
        for t in range(T):
            start = max(0, t - max_notes)
            history[-min(t, max_notes):] = actions[b, start:t, :4].float() if t > 0 else 0
            seq_obs.append(torch.cat([history.flatten(), emotions[b]]))
        obs_list.append(torch.stack(seq_obs))
    obs = torch.stack(obs_list)
    return obs


#------------ PRETRAINING ------------#

def pretrain_with_val(dataset_folder, policy, epochs=100, batch_size=8, lr=1e-3,
                      max_notes=16, num_emotions=3, val_ratio=0.2, device='cpu'):

    dataset = SoundSeqDataset(dataset_folder)
    n_val = int(len(dataset) * val_ratio)
    n_train = len(dataset) - n_val
    train_dataset, val_dataset = random_split(dataset, [n_train, n_val])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)

    ce_losses = [
    nn.CrossEntropyLoss(),                 # Tone (si déjà continu)
    nn.CrossEntropyLoss(),        # Duration
    nn.MSELoss(),                 # Intensity ∈ [0,1]
    nn.CrossEntropyLoss(),        # Flag1
    nn.CrossEntropyLoss()         # Flag2
    ]
    optimizer = optim.Adam(policy.parameters(), lr=lr)
    policy.to(device)

    train_losses, val_losses, spef_losses = [], [], [[], [], [], [], []]

    for epoch in range(epochs):
        # ----- TRAIN -----
        policy.train()
        epoch_losses_train = [0.0] * 5
        total_loss_train = 0.0
        num_batches = 0

        for emotions, actions, lengths in train_loader:
            obs = build_obs(emotions, actions, max_notes).to(device)
            actions = actions.to(device)
            lengths = lengths.to(device)

            optimizer.zero_grad()
            logits = policy(obs, lengths)

            losses_per_dim, total_loss = compute_losses(logits, actions, lengths, ce_losses)
            total_loss.backward()
            optimizer.step()

            for i in range(5):
                epoch_losses_train[i] += losses_per_dim[i].item()
            total_loss_train += total_loss.item()
            num_batches += 1

        epoch_losses_train = [l / num_batches for l in epoch_losses_train]
        epoch_total_train = sum(epoch_losses_train)
        train_losses.append(epoch_total_train)

        # ----- VALIDATION -----
        policy.eval()
        epoch_losses_val = [0.0] * 5
        total_loss_val = 0.0
        num_batches_val = 0

        with torch.no_grad():
            for emotions, actions, lengths in val_loader:
                obs = build_obs(emotions, actions, max_notes).to(device)
                actions = actions.to(device)
                lengths = lengths.to(device)

                logits = policy(obs, lengths)
                losses_per_dim, total_loss = compute_losses(logits, actions, lengths, ce_losses)

                for i in range(5):
                    epoch_losses_val[i] += losses_per_dim[i].item()
                total_loss_val += total_loss.item()
                num_batches_val += 1

        epoch_losses_val = [l / num_batches_val for l in epoch_losses_val]
        epoch_total_val = sum(epoch_losses_val)
        val_losses.append(epoch_total_val)
        for i in range(5):
            spef_losses[i].append(epoch_losses_val[i])

        # ----- AFFICHAGE -----
        print(
            f"Epoch {epoch+1}/{epochs} | "
            f"Train Total: {epoch_total_train:.4f} | "
            f"Val Total: {epoch_total_val:.4f} | "
            f"Tone: {epoch_losses_val[0]:.4f} | "
            f"Duration: {epoch_losses_val[1]:.4f} | "
            f"Intensity: {epoch_losses_val[2]:.4f} | "
            f"Flag1: {epoch_losses_val[3]:.4f} | "
            f"Flag2: {epoch_losses_val[4]:.4f}"
        )

    return train_losses, val_losses, spef_losses


#------------ PLOT FUNCTIONS ------------#

def plot_losses(train_losses, val_losses):
    plt.figure(figsize=(8,5))
    plt.plot(train_losses, label='Train Loss', marker='o')
    plt.plot(val_losses, label='Validation Loss', marker='x')
    plt.xlabel('Epoch')
    plt.ylabel('Total Loss')
    plt.title('Loss curves')
    plt.legend()
    plt.grid(True)
    plt.show()


def param_losses(spef_losses):
    plt.figure(figsize=(8,5))
    labels = ["Tone", "Duration", "Intensity", "Flag1", "Flag2"]
    for i in range(5):
        plt.plot(range(len(spef_losses[i])), spef_losses[i], label=labels[i])
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Loss per output parameter')
    plt.legend()
    plt.grid(True)
    plt.show()


#------------ EXECUTION ------------#

if __name__ == "__main__":
    with Path("sound_config.json").open("r", encoding="utf-8") as f:
        json_content = json.load(f)
        max_notes = json_content["MAX_NOTES"]

    num_emotions = 3
    obs_dim = max_notes * 4 + num_emotions

    policy = PretrainPolicy(obs_dim=obs_dim)

    train_losses, val_losses, spef_losses = pretrain_with_val(
        dataset_folder="dataset/labeled/note_sequences/",
        policy=policy,
        epochs=400,
        batch_size=15,
        lr=1e-4,
        max_notes=max_notes,
        num_emotions=num_emotions,
        val_ratio=0.2,
        device='cpu'
    )

    plot_losses(train_losses, val_losses)
    param_losses(spef_losses)

    # Save model
    torch.save(policy.state_dict(), "pretrained_policy.pt")
