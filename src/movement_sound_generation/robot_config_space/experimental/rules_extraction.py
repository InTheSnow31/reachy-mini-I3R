import json
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ========= CHARGEMENT DES DATASETS =========

def load_dataset(path):
    with open(path) as f:
        raw = json.load(f)

    rows = []
    for d in raw:
        p = d["pose"]
        rows.append({
            "x": p["x"],
            "y": p["y"],
            "z": p["z"],
            "roll": p["roll"],
            "pitch": p["pitch"],
            "yaw": p["yaw"],
            "label": d["label"],
            "id": d.get("id"),
        })
    return pd.DataFrame(rows)


df2 = load_dataset("pose_datasets/pose_dataset_2.json")
df3 = load_dataset("pose_datasets/pose_dataset_3.json")

# fusion
df = pd.concat([df2, df3], ignore_index=True)

# uniquement poses atteignables
ok = df[df["label"] == 1]

# ========= EXTRACTION DES RÈGLES =========

rules = {}

# z → pitch
X = ok[["z"]].values
y = ok["pitch"].values
m = LinearRegression().fit(X, y) # type: ignore
rules["pitch_from_z"] = {
    "a": float(m.coef_[0]),
    "b": float(m.intercept_),
    "sigma": float(np.std(y - m.predict(X))),
}

# y → roll
X = ok[["y"]].values
y = ok["roll"].values
m = LinearRegression().fit(X, y) # type: ignore
rules["roll_from_y"] = {
    "a": float(m.coef_[0]),
    "b": float(m.intercept_),
    "sigma": float(np.std(y - m.predict(X))),
}

# x → yaw (sans body_yaw)
X = ok[["x"]].values
y = ok["yaw"].values
m = LinearRegression().fit(X, y) # type: ignore
rules["yaw_from_x"] = {
    "a": float(m.coef_[0]),
    "b": float(m.intercept_),
    "sigma": float(np.std(y - m.predict(X))),
}

# ========= SAUVEGARDE =========

with open("rules/rules_3.json", "w") as f:
    json.dump(rules, f, indent=2)
