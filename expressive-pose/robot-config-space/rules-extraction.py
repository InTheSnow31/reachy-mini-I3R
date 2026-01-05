import pandas as pd
import numpy as np
import json
from sklearn.linear_model import LinearRegression

with open("pose_dataset_2.json") as f:
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
        "body_yaw": p["body_yaw"],
        "ant_a": p["antennas"][0],
        "ant_b": p["antennas"][1],
        "label": d["label"],
        "id": d.get("id"),
    })

df = pd.DataFrame(rows)

ok = df[df["label"] == 1]

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

# x, body_yaw → yaw
X = ok[["x", "body_yaw"]].values
y = ok["yaw"].values
m = LinearRegression().fit(X, y) # type: ignore
rules["yaw_from_x_body"] = {
    "a_x": float(m.coef_[0]),
    "a_body": float(m.coef_[1]),
    "b": float(m.intercept_),
    "sigma": float(np.std(y - m.predict(X))),
}

# sauvegarde
import json
with open("rules.json", "w") as f:
    json.dump(rules, f, indent=2)
