"""
A pour objectif de transformer les sons d'une base de données en encodage souhaité pour la synthèse sonore.
"""

import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
import sounddevice as sd

def synthetiser_fondamentales(
    fondamentales: list,
    duree_fenetre: float,
    fs: int = 44100,
    amplitude: float = 0.8,
    sortie_wav: str | None = "fondamentales.wav",
    jouer: bool = True
):
    """
    Génère un signal audio ne contenant que les fondamentales.
    """

    signal_total = []
    phase = 0.0

    for f0 in fondamentales:
        nb_samples = int(duree_fenetre * fs)

        if f0 is None or f0 <= 0:
            frame = np.zeros(nb_samples)
        else:
            t = np.arange(nb_samples) / fs
            frame = amplitude * np.sin(2 * np.pi * f0 * t + phase)

            # Continuité de phase
            phase += 2 * np.pi * f0 * duree_fenetre
            phase = phase % (2 * np.pi)

        signal_total.append(frame)

    signal = np.concatenate(signal_total)

    # Normalisation
    signal /= np.max(np.abs(signal)) + 1e-12

    # Sauvegarde WAV
    if sortie_wav is not None:
        wav.write(
            sortie_wav,
            fs,
            (signal * 32767).astype(np.int16)
        )

    # Lecture audio
    if jouer:
        sd.play(signal, fs)
        sd.wait()

    return signal



def fondamentale_par_fenetre(
    fichier_wav: str,
    duree_fenetre: float = 0.05,
    fmin: float = 50.0,
    fmax: float = 1000.0,
    afficher: bool = True
):

    # Lecture WAV
    fs, signal = wav.read(fichier_wav)     #fs : fréquence d'échantillonnage
    if signal.ndim > 1: # Conversion mono
        signal = signal.mean(axis=1)

    signal = signal.astype(np.float64)
    signal /= np.max(np.abs(signal)) #Normalisation

    taille_fenetre = int(duree_fenetre * fs)
    nb_fenetres = len(signal) // taille_fenetre

    fondamentales = []

    for i in range(nb_fenetres):
        debut = i * taille_fenetre
        fin = debut + taille_fenetre
        frame = signal[debut:fin]

        frame *= np.hanning(len(frame)) # Fenêtre de Hann

        fondamentales.append(estimer_fondamentale_autocorrelation(frame, fs, fmin, fmax))

    if afficher:
        temps = np.arange(nb_fenetres) * duree_fenetre
        plt.figure(figsize=(10, 4))
        plt.plot(temps, fondamentales, marker='o')
        plt.xlabel("Temps (s)")
        plt.ylabel("Fréquence fondamentale (Hz)")
        plt.title("Évolution temporelle de la fondamentale")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    return fs, fondamentales

def estimer_fondamentale_autocorrelation(
    frame: np.ndarray,
    fs: int,
    fmin: float,
    fmax: float
) -> float | None:
    """
    Estime la fréquence fondamentale d'une trame
    par autocorrélation.
    """

    # Autocorrélation
    corr = np.correlate(frame, frame, mode='full')
    corr = corr[len(corr)//2:]

    # Suppression du pic à zéro
    corr[0] = 0

    # Bornes de recherche (lags)
    lag_min, lag_max = int(fs / fmax), int(fs / fmin)

    if lag_max >= len(corr):
        return None

    lag = np.argmax(corr[lag_min:lag_max]) + lag_min

    f0 = fs / lag

    return f0

fs_source, fonds = fondamentale_par_fenetre("dataset/labeled/sounds/VO_02_018.dspadpcm.wav")
synthetiser_fondamentales(fonds, duree_fenetre=0.05, sortie_wav=None, jouer=True, fs=fs_source)