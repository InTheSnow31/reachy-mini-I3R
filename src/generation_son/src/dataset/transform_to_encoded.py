"""
A pour objectif de transformer les sons d'une base de données en encodage souhaité pour la synthèse sonore.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
import json
import math

from synthesis.notes_to_wave import notes_to_wav
from Note import Note


def extract_f0s(
    fichier_wav: str,
    duree_fenetre: float = 0.02,
    fmin: float = 100.0,
    fmax: float = 1000.0,
    tolerance_hz: float = 2.0,
    seuil_energie: float = 0.10
):
    """
    WAV → fondamentales (début, durée, fréquence, intensité)
    """

    fs, signal = wav.read(fichier_wav) #fs = fréquence échantillonage

    if signal.ndim > 1: #Son stéréo --> mono
        signal = signal.mean(axis=1)

    signal = np.abs(signal.astype(np.float64))
    signal /= np.max(signal) + 1e-12 #Normalisation

    taille_fenetre = int(duree_fenetre * fs)
    nb_fenetres = len(signal) // taille_fenetre

    f0_par_fenetre = []
    rms_par_fenetre = []

    # Analyse par fenêtres
    for i in range(nb_fenetres):
        frame = signal[(i * taille_fenetre): ((i+1) * taille_fenetre)]

        # Intensité moyenne
        rms = np.sqrt(np.mean(frame ** 2))
        rms_par_fenetre.append(rms)

        # Supression des silences
        if rms < seuil_energie:
            f0_par_fenetre.append(None)
            continue

        frame *= np.hanning(len(frame)) # Réduit effets de bords
        f0 = estimate_f0(frame, fs, fmin, fmax) # Auto-corrélation
        f0_par_fenetre.append(f0)

    # Regroupement 
    evenements = group_f0s_intensities(f0_par_fenetre, rms_par_fenetre, duree_fenetre, tolerance_hz)

    return evenements

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
    duree_fenetre,
    tolerance_hz
):
    evenements = []

    freq_courante = None
    debut = None
    nb = 0
    intensites = []

    for i, (f0, r) in enumerate(zip(f0s, rms)):
        t = i * duree_fenetre

        if f0 is None:
            if freq_courante is not None:
                evenements.append((debut, nb * duree_fenetre, freq_courante, float(np.mean(intensites))))
                freq_courante = None
                nb = 0
                intensites = []
            continue

        if freq_courante is None:
            freq_courante = f0
            debut = t
            nb = 1
            intensites = [r]

        elif abs(f0 - freq_courante) <= tolerance_hz:
            nb += 1
            intensites.append(r)
        else:
            evenements.append((
                debut,
                nb * duree_fenetre,
                freq_courante,
                float(np.mean(intensites))
            ))
            freq_courante = f0
            debut = t
            nb = 1
            intensites = [r]

    if freq_courante is not None:
        evenements.append((debut, nb * duree_fenetre, freq_courante, float(np.mean(intensites))))

    return evenements

def display_f0s(evenements, afficher_intensite: bool = True, cmap: str = "viridis"):
    """
    Affiche les événements de fondamentales avec intensité.
    """

    fig, ax = plt.subplots(figsize=(10, 4))

    intensites = [e[3] for e in evenements] if afficher_intensite else None
    vmin = min(intensites) if afficher_intensite else None
    vmax = max(intensites) if afficher_intensite else None

    for debut, duree, freq, intensite in evenements:
        if afficher_intensite:
            couleur = plt.cm.get_cmap(cmap)(
                (intensite - vmin) / (vmax - vmin + 1e-12)
            )
            epaisseur = 2 + 6 * (intensite - vmin) / (vmax - vmin + 1e-12)
        else:
            couleur = "blue"
            epaisseur = 2

        ax.hlines(
            y=freq,
            xmin=debut,
            xmax=debut + duree,
            linewidth=epaisseur,
            color=couleur
        )

    ax.set_xlabel("Temps (s)")
    ax.set_ylabel("Fréquence fondamentale (Hz)")
    ax.set_title("Évolution temporelle des fondamentales")
    ax.grid(True, alpha=0.3)

    # --- Colorbar correctement attachée ---
    if afficher_intensite:
        sm = plt.cm.ScalarMappable(
            cmap=cmap,
            norm=plt.Normalize(vmin=vmin, vmax=vmax)
        )
        sm.set_array([])
        fig.colorbar(sm, ax=ax, label="Intensité (RMS)")

    plt.tight_layout()
    plt.show()

def display_formated(notes):
    current_x = 0
    i = 0
    while i < len(notes) :
        if notes[i].slide : #Sliding == "True"
            plt.plot([current_x, current_x + notes[i].duration], [notes[i].pitch, notes[i+1].pitch], marker='o', linestyle='-')
            current_x += notes[i].duration + notes[i+1].duration
            i += 2
        else :
            plt.plot([current_x], [notes[i].pitch], marker='o', linestyle='None')
            current_x += notes[i].duration
            i += 1
    plt.grid(True)
    plt.show()

def synthesize_f0_events(
    evenements,
    fs: int = 44100,
    gain: float = 0.9,
    attaque: float = 0.01,
    relache: float = 0.02,
    fichier_sortie: str = "tests/synthese.wav"
):
    """
    Synthétise un WAV à partir d'événements (t, d, f0, intensité).

    evenements : liste de tuples (debut, duree, freq, intensite)
    fs         : fréquence d'échantillonnage
    gain       : gain global
    attaque    : temps d'attaque (s)
    relache    : temps de relâche (s)
    """

    # --- Durée totale ---
    duree_totale = max(t + d for t, d, _, _ in evenements)
    n_samples = int(duree_totale * fs) + 1
    signal = np.zeros(n_samples)

    for debut, duree, freq, intensite in evenements:
        if freq <= 0 or duree <= 0:
            continue

        n = int(duree * fs)
        t = np.arange(n) / fs

        # --- Oscillateur ---
        osc = np.sin(2 * np.pi * freq * t)

        # --- Enveloppe ADSR simplifiée ---
        n_att = int(attaque * fs)
        n_rel = int(relache * fs)

        env = np.ones(n)
        if n_att > 0:
            env[:n_att] = np.linspace(0, 1, n_att)
        if n_rel > 0:
            env[-n_rel:] = np.linspace(1, 0, n_rel)

        # --- Signal événement ---
        evt = osc * env * intensite

        # --- Insertion temporelle ---
        i0 = int(debut * fs)
        signal[i0:i0+n] += evt

    # --- Normalisation ---
    max_val = np.max(np.abs(signal)) + 1e-12
    signal = gain * signal / max_val

    # --- Conversion int16 ---
    signal_int16 = np.int16(signal * 32767)

    wav.write(fichier_sortie, fs, signal_int16)

    print(f"WAV généré : {fichier_sortie}")

def detecte_sliding(evenements, tolerance_derivative = 2):
    times = [evenement[0] for evenement in evenements]
    fondamentales = [evenement[2] for evenement in evenements]
    intensities = [evenement[3] for evenement in evenements]
    current_sliding = []
    final_values = []
    for i in range(len(fondamentales)):
        if len(current_sliding) <= 1 :
            current_sliding.append([times[i],fondamentales[i], intensities[i]])
        else :
            previous_dy = (fondamentales[i-1] - fondamentales[i-2])/(times[i-1]-times[i-2])
            current_dy = (fondamentales[i] - fondamentales[i-1])/(times[i]-times[i-1]) 
            if 1/tolerance_derivative < (current_dy / previous_dy) < tolerance_derivative :
                current_sliding.append([times[i],fondamentales[i], intensities[i]])
            #Cas où la tolérance est dépassée --> Fin du slide
            else :
                if len(current_sliding) > 2 :
                    borne_inf = current_sliding[0]
                    borne_sup = current_sliding[-1]
                    final_values.append(borne_inf + [True])
                    final_values.append(borne_sup + [False])
                else :
                    for note in current_sliding :
                        final_values.append(note + [False])
                current_sliding = []
                current_sliding.append([times[i],fondamentales[i], intensities[i]])
    return final_values

def nearest_duration(duration, bpm, duration_scale) :
    timespace = 60 / bpm #en seconde
    quotient = duration // timespace
    reste = duration % timespace
    value = 0
    if (duration - reste) > reste : # Plus proche de reste que de duration
        value = quotient
    else :
        value =  quotient + 1
    
    return min(value, duration_scale)

def nearest_note(f):
    n = 1 + 12 * math.log2(f / 27.5)
    n = round(n)           # touche entière la plus proche
    n = max(1, min(88, n)) # limiter entre 1 et 88
    return n

def tempo_ajusted(notes_with_slidings, bpm, duration_scale):
    times = [note[0] for note in notes_with_slidings]
    fondamentales = [note[1] for note in notes_with_slidings]
    intensities = [note[2] for note in notes_with_slidings]
    sliding = [note[3] for note in notes_with_slidings]
    formated = []
    for i in range(len(notes_with_slidings)-1) :
        #différences entre la note et la prochaine note
        duration = times[i+1] - times[i]
        print(duration)
        formated_duration = nearest_duration(duration, bpm, duration_scale)
        formated_note = nearest_note(fondamentales[i])
        formated.append(Note(formated_note, intensities[i], formated_duration, sliding[i]))
    return formated

# RECUPERATION DATA
with Path("sound_config.json").open("r", encoding="utf-8") as f:
    content = json.load(f)
    bpm = content["BPM"]
    duration_scale = content["DURATION_SCALE"]

#APPEL DES FONCTION

evenements = extract_f0s("dataset/labeled/sounds/VO_02_018.dspadpcm.wav", 
    duree_fenetre = 60/bpm/2,
    fmin = 100.0,
    fmax = 800.0,
    seuil_energie = 0.10
)
display_f0s(evenements, afficher_intensite=True)
synthesize_f0_events(evenements, fs=44100, fichier_sortie="tests/reconstruction.wav")

slidings_detected = detecte_sliding(evenements, tolerance_derivative=2)
encoded = tempo_ajusted(slidings_detected, bpm=bpm, duration_scale=duration_scale)
for note in encoded : 
    print(note)
notes_to_wav(encoded, "tests/results.wav", bpm=bpm)
display_formated(encoded)

