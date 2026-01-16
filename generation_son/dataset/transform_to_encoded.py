"""
A pour objectif de transformer les sons d'une base de données en encodage souhaité pour la synthèse sonore.
"""

import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt

def extract_f0s(
    fichier_wav: str,
    duree_fenetre: float = 0.03,
    fmin: float = 50.0,
    fmax: float = 1000.0,
    tolerance_hz: float = 2.0,
    seuil_energie: float = 0.01
):
    """
    WAV → événements (début, durée, fréquence, intensité)
    """

    fs, signal = wav.read(fichier_wav)

    if signal.ndim > 1:
        signal = signal.mean(axis=1)

    signal = signal.astype(np.float64)
    signal /= np.max(np.abs(signal)) + 1e-12

    taille_fenetre = int(duree_fenetre * fs)
    nb_fenetres = len(signal) // taille_fenetre

    f0_par_fenetre = []
    rms_par_fenetre = []

    # --- Analyse par fenêtres ---
    for i in range(nb_fenetres):
        debut = i * taille_fenetre
        fin = debut + taille_fenetre
        frame = signal[debut:fin]

        rms = np.sqrt(np.mean(frame ** 2))
        rms_par_fenetre.append(rms)

        if rms < seuil_energie:
            f0_par_fenetre.append(None)
            continue

        frame *= np.hanning(len(frame))
        f0 = estimate_f0(frame, fs, fmin, fmax)
        f0_par_fenetre.append(f0)

    # --- Regroupement ---
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

    if not evenements:
        print("Aucun événement à afficher.")
        return

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


evenements = extract_f0s("dataset/labeled/sounds/VO_02_018.dspadpcm.wav")
for t, d, f, i in evenements:
    print(f"t={t:.2f}s | d={d:.2f}s | f0={f:.1f} Hz | I={i:.3f}")

display_f0s(evenements, afficher_intensite=True)