from pydub import AudioSegment
from pathlib import Path

# Chemins
MP3_PATH = Path("dataset/labeled/sounds/")
WAV_PATH = Path("dataset/labeled/sounds/")
WAV_PATH.mkdir(parents=True, exist_ok=True)

# Parcours de tous les mp3
for mp3_file in MP3_PATH.glob("*.mp3"):
    wav_file = WAV_PATH / f"{mp3_file.stem}.wav"
    
    # Conversion
    audio = AudioSegment.from_file(mp3_file, format="mp3")
    audio.export(wav_file, format="wav")

    print(f"{mp3_file.name} → {wav_file.name}")