#------------- IMPORTS -------------#

import torch
from torch import nn, optim
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence, pad_packed_sequence
from torch.utils.data import Dataset, DataLoader, random_split
from pathlib import Path
import matplotlib.pyplot as plt
import json


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
                json_content["MAX_NOTES"],
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
        self.heads = nn.ModuleList(
            [nn.Linear(hidden_dim, dim) for dim in action_dims]
        )
    
    def forward(self, x, lengths):
        packed = pack_padded_sequence(
            x,
            lengths.cpu(),
            batch_first=True,
            enforce_sorted=False
        )
        packed_out, _ = self.lstm(packed)
        out, _ = pad_packed_sequence(packed_out, batch_first=True)
        logits = [head(out) for head in self.heads]  # list of (batch, seq_len, dim)
        return logits


#---------- PRETRAINING ----------#

def pretrain_with_val(
    dataset_folder,
    policy,
    epochs=100,
    batch_size=8,
    lr=1e-3,
    max_notes=16,
    num_emotions=3,
    val_ratio=0.2,
    device='cpu'
):
    # Load dataset
    dataset = SoundSeqDataset(dataset_folder)
    n_val = int(len(dataset) * val_ratio)
    n_train = len(dataset) - n_val
    train_dataset, val_dataset = random_split(dataset, [n_train, n_val])

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_fn
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate_fn
    )

    optimizer = optim.Adam(policy.parameters(), lr=lr)
    ce_losses = [nn.CrossEntropyLoss() for _ in range(5)]  # 5 MultiDiscrete dimensions

    policy.to(device)

    train_losses = []
    val_losses = []

    for epoch in range(epochs):
        # ----- Training -----
        policy.train()
        total_loss = 0

        for emotions, actions, lengths in train_loader:
            batch_size_, seq_len, _ = actions.shape
            obs = []

            for b in range(batch_size_):
                history = torch.zeros(max_notes, 4)
                seq_obs = []

                for t in range(seq_len):
                    start = max(0, t - max_notes)
                    history[-min(t, max_notes):] = (
                        actions[b, start:t, :4].float() if t > 0 else 0
                    )
                    seq_obs.append(
                        torch.cat([history.flatten(), emotions[b]])
                    )

                obs.append(torch.stack(seq_obs))

            obs = torch.stack(obs).to(device)
            actions = actions.to(device)

            optimizer.zero_grad()
            logits = policy(obs, lengths.to(device))

            loss = 0
            for i, logit in enumerate(logits):
                logit_flat = logit.view(-1, logit.shape[-1])
                target_flat = actions[:, :, i].reshape(-1)
                loss += ce_losses[i](logit_flat, target_flat)

            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_train_loss = total_loss / len(train_loader)
        train_losses.append(avg_train_loss)

        # ----- Validation -----
        policy.eval()
        val_loss_total = 0

        with torch.no_grad():
            for emotions, actions, lengths in val_loader:
                batch_size_, seq_len, _ = actions.shape
                obs = []

                for b in range(batch_size_):
                    history = torch.zeros(max_notes, 4)
                    seq_obs = []

                    for t in range(seq_len):
                        start = max(0, t - max_notes)
                        history[-min(t, max_notes):] = (
                            actions[b, start:t, :4].float() if t > 0 else 0
                        )
                        seq_obs.append(
                            torch.cat([history.flatten(), emotions[b]])
                        )

                    obs.append(torch.stack(seq_obs))

                obs = torch.stack(obs).to(device)
                actions = actions.to(device)

                logits = policy(obs, lengths.to(device))
                val_loss = 0

                for i, logit in enumerate(logits):
                    logit_flat = logit.view(-1, logit.shape[-1])
                    target_flat = actions[:, :, i].reshape(-1)
                    val_loss += ce_losses[i](logit_flat, target_flat)

                val_loss_total += val_loss.item()

        avg_val_loss = val_loss_total / len(val_loader)
        val_losses.append(avg_val_loss)

        print(
            f"Epoch {epoch+1}/{epochs}, "
            f"Train Loss: {avg_train_loss:.4f}, "
            f"Val Loss: {avg_val_loss:.4f}"
        )

    print("Pretraining completed!")
    return train_losses, val_losses


def plot_losses(train_losses, val_losses):
    """
    Display training and validation loss curves.

    train_losses, val_losses: lists of floats, length = number of epochs
    """
    plt.figure(figsize=(8, 5))
    plt.plot(train_losses, label="Train Loss", marker='o')
    plt.plot(val_losses, label="Validation Loss", marker='x')
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Loss curves")
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

    train_losses, val_losses = pretrain_with_val(
        dataset_folder="dataset/labeled/note_sequences/",
        policy=policy,
        epochs=350,
        batch_size=15,
        lr=1e-3,
        max_notes=max_notes,
        num_emotions=num_emotions,
        val_ratio=0.2,
        device='cpu'
    )

    plot_losses(train_losses, val_losses)

    # Save
    torch.save(policy.state_dict(), "pretrained_policy.pt")
