import json
import sys
from pathlib import Path


def normalize_pad(value: float) -> float:
    """Map [-1, 1] -> [0, 1] with clipping."""
    return max(0.0, min(1.0, (value + 1.0) * 0.5))


def convert_json(input_path: Path, output_path: Path) -> None:
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Update axis metadata
    data["axes"] = {
        "Pleasure": {"min": 0.0, "max": 1.0},
        "Arousal": {"min": 0.0, "max": 1.0},
        "Dominance": {"min": 0.0, "max": 1.0},
    }

    # Normalize emotions
    for emo, values in data.get("emotions", {}).items():
        for k in ("P", "A", "D"):
            if k in values:
                values[k] = normalize_pad(values[k])

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_pad_json.py input.json output.json")
        sys.exit(1)

    convert_json(Path(sys.argv[1]), Path(sys.argv[2]))
