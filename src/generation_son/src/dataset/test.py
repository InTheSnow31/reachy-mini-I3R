
import librosa
import crepe
import matplotlib.pyplot as plt
import numpy as np

def display_crepe_f0(
    time,
    frequency,
    confidence,
    confidence_threshold: float = 0.5,
    figsize=(12, 5)
):
    """
    Affiche la fréquence fondamentale estimée par CREPE et la confiance associée.

    Parameters
    ----------
    time : array-like
        Temps (s)
    frequency : array-like
        Fréquence fondamentale (Hz)
    confidence : array-like
        Score de confiance (0 à 1)
    confidence_threshold : float
        Seuil minimal de confiance pour afficher la f0
    figsize : tuple
        Taille de la figure matplotlib
    """

    # Masquage des estimations peu fiables
    f0_plot = np.where(confidence >= confidence_threshold, frequency, np.nan)

    plt.figure(figsize=figsize)

    # Axe principal : f0
    plt.plot(time, f0_plot, label="F0 (Hz)")
    plt.xlabel("Temps (s)")
    plt.ylabel("Fréquence fondamentale (Hz)")

    # Axe secondaire : confiance
    ax = plt.gca()
    ax2 = ax.twinx()
    ax2.plot(time, confidence, label="Confidence", alpha=0.5)
    ax2.set_ylabel("Confiance")

    plt.title("Estimation de la fréquence fondamentale (CREPE)")
    ax.grid(True, alpha=0.3)

    # Légende combinée
    lines, labels = [], []
    for a in (ax, ax2):
        l, lab = a.get_legend_handles_labels()
        lines += l
        labels += lab
    ax.legend(lines, labels, loc="upper right")

    plt.tight_layout()
    plt.show()


audio, sr = librosa.load("generation_son/tests/NPC_sound.wav", sr=16000)

time, frequency, confidence, _ = crepe.predict(
    audio,
    sr,
    viterbi=True
)

display_crepe_f0(time, frequency, confidence)
