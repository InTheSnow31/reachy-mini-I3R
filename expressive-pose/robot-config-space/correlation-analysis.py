import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# ========= PARAMETERS =========
DATA_FILE = "pose_dataset_2.json"
PCA_COMPONENTS = 2 
# ==============================

# Dataset
with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# X and y extraction
features = []
labels = []

for entry in data:
    pose = entry["pose"]
    features.append([
        pose["x"], pose["y"], pose["z"],
        pose["roll"], pose["pitch"], pose["yaw"],
        pose["body_yaw"], pose["antennas"][0], pose["antennas"][1]
    ])
    labels.append(entry["label"])

X = np.array(features)
y = np.array(labels)
cols = ["x","y","z","roll","pitch","yaw","body_yaw","ant1","ant2"]
n_features = len(cols)

# PCA
pca = PCA(n_components=PCA_COMPONENTS)
X_scaled = (X - X.mean(axis=0)) / X.std(axis=0)  # standardisation
X_pca = pca.fit_transform(X_scaled)

# Correlation circle
fig, ax = plt.subplots(figsize=(8,8))
ax.set_xlim(-1.1, 1.1)
ax.set_ylim(-1.1, 1.1)
circle = plt.Circle((0,0), 1, color='grey', fill=False, linestyle='--') # pyright: ignore[reportPrivateImportUsage]
ax.add_artist(circle)

# Variables vectors
for i, col_name in enumerate(cols):
    x_vec = pca.components_[0, i]
    y_vec = pca.components_[1, i]
    ax.arrow(0, 0, x_vec, y_vec, color='r', alpha=0.8,
             head_width=0.03, head_length=0.03)
    ax.text(x_vec*1.1, y_vec*1.1, col_name, color='b', ha='center', va='center')

ax.set_xlabel("PC1")
ax.set_ylabel("PC2")
ax.set_title("Correlation circle")
ax.grid(True)
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)
plt.show()

print("Variance explained by PC1 et PC2 :", pca.explained_variance_ratio_)
