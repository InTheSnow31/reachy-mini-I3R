"""
Transform sound into the corresponding encoded note sequence.
"""

#------------- IMPORTS -------------#

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
import torch
import json
import math

from synthesis.synthesize_whistle_with_harmonics import notes_to_wav
from Note import Note


#------- PATHS AND PARAMETERS -------#

OUTPUT_PATH = "dataset/labeled/note_sequences/"
LABELS_PATH = "dataset/labeled/labels/"
SOUND_PATH = "dataset/labeled/sounds/"


#------------ FUNCTIONS ------------#

def extract_f0s(
    wav_file: str,
    window_duration: float = 0.02,
    fmin: float = 100.0,
    fmax: float = 1000.0,
    tolerance_hz: float = 2.0,
    energy_threshold: float = 0.10
):
    """
    WAV → f0s
    """

    fs, signal = wav.read(wav_file)  # fs = sample rate

    if signal.ndim > 1:  # Stereo --> mono
        signal = signal.mean(axis=1)

    signal = np.abs(signal.astype(np.float64))
    signal /= np.max(signal) + 1e-12  # Normalization

    window_size = int(window_duration * fs)
    n_windows = len(signal) // window_size

    f0_per_window = []
    rms_per_window = []

    for i in range(n_windows):
        frame = signal[(i * window_size): ((i+1) * window_size)]

        # Average intensity
        rms = np.sqrt(np.mean(frame ** 2))
        rms_per_window.append(rms)

        # Silence removal
        if rms < energy_threshold:
            f0_per_window.append(None)
            continue

        frame *= np.hanning(len(frame))  # Reduce edge effects
        f0 = estimate_f0(frame, fs, fmin, fmax)  # Auto-correlation
        f0_per_window.append(f0)

    # Grouping
    events = group_f0s_intensities(f0_per_window, rms_per_window, window_duration, tolerance_hz)

    return events

def estimate_f0(frame, fs, fmin, fmax):
    corr = np.correlate(frame, frame, mode="full")
    corr = corr[len(corr)//2:]
    corr[0] = 0

    lag_min = int(fs / fmax)
    lag_max = int(fs / fmin)

    if lag_max >= len(corr):
        return None

    lag = np.argmax(corr[lag_min:lag_max]) + lag_min
    return fs / lag

def group_f0s_intensities(
    f0s,
    rms,
    window_duration,
    tolerance_hz
):
    events = []

    current_freq = None
    start_time = None
    count = 0
    intensities = []

    for i, (f0, r) in enumerate(zip(f0s, rms)):
        t = i * window_duration

        if f0 is None:
            if current_freq is not None:
                events.append((start_time, count * window_duration, current_freq, float(np.mean(intensities))))
                current_freq = None
                count = 0
                intensities = []
            continue

        if current_freq is None:
            current_freq = f0
            start_time = t
            count = 1
            intensities = [r]

        elif abs(f0 - current_freq) <= tolerance_hz:
            count += 1
            intensities.append(r)
        else:
            events.append((
                start_time,
                count * window_duration,
                current_freq,
                float(np.mean(intensities))
            ))
            current_freq = f0
            start_time = t
            count = 1
            intensities = [r]

    if current_freq is not None:
        events.append((start_time, count * window_duration, current_freq, float(np.mean(intensities))))

    return events

def display_f0s(events, show_intensity: bool = True, cmap: str = "viridis"):
    """
    Display fundamental frequency events with intensity.
    """

    fig, ax = plt.subplots(figsize=(10, 4))

    intensities = [e[3] for e in events] if show_intensity else None
    vmin = min(intensities) if show_intensity else None
    vmax = max(intensities) if show_intensity else None

    for start, duration, freq, intensity in events:
        if show_intensity:
            color = plt.cm.get_cmap(cmap)(
                (intensity - vmin) / (vmax - vmin + 1e-12)
            )
            linewidth = 2 + 6 * (intensity - vmin) / (vmax - vmin + 1e-12)
        else:
            color = "blue"
            linewidth = 2

        ax.hlines(
            y=freq,
            xmin=start,
            xmax=start + duration,
            linewidth=linewidth,
            color=color
        )

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Fundamental frequency (Hz)")
    ax.set_title("Temporal evolution of fundamentals")
    ax.grid(True, alpha=0.3)

    # --- Properly attached colorbar ---
    if show_intensity:
        sm = plt.cm.ScalarMappable(
            cmap=cmap,
            norm=plt.Normalize(vmin=vmin, vmax=vmax)
        )
        sm.set_array([])
        fig.colorbar(sm, ax=ax, label="Intensity (RMS)")

    plt.tight_layout()
    plt.show()

def display_formatted(notes):
    current_x = 0
    i = 0
    while i < len(notes):
        if notes[i].slide:  # Sliding == True
            plt.plot([current_x, current_x + notes[i].duration], [notes[i].pitch, notes[i+1].pitch], marker='o', linestyle='-')
            current_x += notes[i].duration + notes[i+1].duration
            i += 2
        else:
            plt.plot([current_x], [notes[i].pitch], marker='o', linestyle='None')
            current_x += notes[i].duration
            i += 1
    plt.grid(True)
    plt.show()

def synthesize_f0_events(
    events,
    fs: int = 44100,
    gain: float = 0.9,
    attack: float = 0.01,
    release: float = 0.02,
    output_file: str = "tests/synthesized.wav"
):
    """
    Synthesize a WAV from events (start_time, duration, f0, intensity).

    events      : list of tuples (start_time, duration, freq, intensity)
    fs          : sampling rate
    gain        : global gain
    attack      : attack time (s)
    release     : release time (s)
    """

    # --- Total duration ---
    total_duration = max(t + d for t, d, _, _ in events)
    n_samples = int(total_duration * fs) + 1
    signal = np.zeros(n_samples)

    for start, duration, freq, intensity in events:
        if freq <= 0 or duration <= 0:
            continue

        n = int(duration * fs)
        t = np.arange(n) / fs

        # --- Oscillator ---
        osc = np.sin(2 * np.pi * freq * t)

        # --- Simplified ADSR envelope ---
        n_att = int(attack * fs)
        n_rel = int(release * fs)

        env = np.ones(n)
        if n_att > 0:
            env[:n_att] = np.linspace(0, 1, n_att)
        if n_rel > 0:
            env[-n_rel:] = np.linspace(1, 0, n_rel)

        # --- Event signal ---
        evt = osc * env * intensity

        # --- Insert into signal ---
        i0 = int(start * fs)
        signal[i0:i0+n] += evt

    # --- Normalization ---
    max_val = np.max(np.abs(signal)) + 1e-12
    signal = gain * signal / max_val

    # --- Convert to int16 ---
    signal_int16 = np.int16(signal * 32767)

    wav.write(output_file, fs, signal_int16)

    print(f"WAV generated: {output_file}")

def detect_sliding(events, derivative_tolerance=2):
    times = [event[0] for event in events]
    fundamentals = [event[2] for event in events]
    intensities = [event[3] for event in events]
    current_slide = []
    final_values = []
    for i in range(len(fundamentals)):
        if len(current_slide) <= 1:
            current_slide.append([times[i], fundamentals[i], intensities[i]])
        else:
            prev_dy = (fundamentals[i-1] - fundamentals[i-2]) / (times[i-1] - times[i-2])
            curr_dy = (fundamentals[i] - fundamentals[i-1]) / (times[i] - times[i-1])
            if 1/derivative_tolerance < (curr_dy / prev_dy) < derivative_tolerance:
                current_slide.append([times[i], fundamentals[i], intensities[i]])
            else:
                if len(current_slide) > 2:
                    lower_bound = current_slide[0]
                    upper_bound = current_slide[-1]
                    final_values.append(lower_bound + [True])
                    final_values.append(upper_bound + [False])
                else:
                    for note in current_slide:
                        final_values.append(note + [False])
                current_slide = []
                current_slide.append([times[i], fundamentals[i], intensities[i]])
    return final_values

def nearest_duration(duration, bpm, duration_scale):
    beat_time = 60 / bpm  # in seconds
    quotient = duration // beat_time
    remainder = duration % beat_time
    value = 0
    if (duration - remainder) > remainder:
        value = quotient
    else:
        value = quotient + 1

    return min(value, duration_scale)

def nearest_note(frequency):
    n = 1 + 12 * math.log2(frequency / 27.5)
    n = round(n)
    n = max(1, min(88, n))  # limit between 1 and 88
    return n

def tempo_adjusted(notes_with_slides, bpm, duration_scale):
    times = [note[0] for note in notes_with_slides]
    fundamentals = [note[1] for note in notes_with_slides]
    intensities = [note[2] for note in notes_with_slides]
    slides = [note[3] for note in notes_with_slides]
    formatted = []
    for i in range(len(notes_with_slides)-1):
        duration = times[i+1] - times[i]
        formatted_duration = nearest_duration(duration, bpm, duration_scale)
        formatted_note = nearest_note(fundamentals[i])
        formatted.append(Note(formatted_note, intensities[i], formatted_duration, slides[i]))
    return formatted

# LOAD CONFIGURATION
with Path("sound_config.json").open("r", encoding="utf-8") as f:
    content = json.load(f)
    bpm = content["BPM"]
    duration_scale = content["DURATION_SCALE"]

# FUNCTION CALL

def transform_to_encoded(source_name, output_path=OUTPUT_PATH):
    audio_file = SOUND_PATH + source_name + ".wav"
    events = extract_f0s(
        audio_file,
        window_duration=60/bpm/2,
        fmin=100.0,
        fmax=800.0,
        energy_threshold=0.10
    )

    # display_f0s(events, show_intensity=True)
    # synthesize_f0_events(events, fs=44100, output_file="tests/reconstruction.wav")

    slides_detected = detect_sliding(events, derivative_tolerance=2)
    encoded = tempo_adjusted(slides_detected, bpm=bpm, duration_scale=duration_scale)

    with open(LABELS_PATH+source_name+".txt", "r", encoding="utf-8") as f:
        emotions = f.read()
        emotions = [float(e) for e in emotions.split(",")]

    # Saving

    sequence_notes = [list(en) + [0] for en in encoded]
    sequence_notes[-1][-1] = 1  # mark the last done as True

    data = {
        "emotion": torch.tensor(emotions, dtype=torch.float32),
        "actions": torch.tensor(sequence_notes, dtype=torch.long)
    }

    assert data["emotion"].shape == (3,)
    assert data["actions"].ndim == 2
    assert data["actions"].shape[1] == 5
    assert data["actions"].dtype == torch.long
    torch.save(data, OUTPUT_PATH + f"seq_{source_name}.pt")


#------------ EXECUTION ------------#

label_files = sorted(Path(LABELS_PATH).glob("*.txt"))
for label_file in label_files:
    source_name = label_file.stem  # name without extension
    transform_to_encoded(source_name)
