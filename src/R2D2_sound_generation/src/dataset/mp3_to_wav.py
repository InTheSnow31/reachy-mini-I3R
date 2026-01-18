#------------- IMPORTS -------------#

from pydub import AudioSegment
from pathlib import Path

#------- PATHS AND PARAMETERS -------#

FOLDER_PATH = Path("dataset/labeled/sounds/")

#------------ EXECUTION ------------#

for mp3_file in FOLDER_PATH.glob("*.mp3"):
    wav_file = FOLDER_PATH / f"{mp3_file.stem}.wav"
    audio = AudioSegment.from_file(mp3_file, format="mp3")
    audio.export(wav_file, format="wav")

    print(f"{mp3_file.name} → {wav_file.name}")