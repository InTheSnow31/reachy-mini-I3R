import tkinter as tk
import tkinter.font as tkfont
from PIL import Image, ImageTk
import math
import sounddevice as sd
import soundfile as sf
from emotion import polar_to_emotion

WINDOW_SIZE = 800
CANVAS_SIZE = 700
IMAGE_PATH = "wheel.png"
POINT_RADIUS = 5
WAV_FILE = "temp.wav"  # fichier à jouer

class input:
    def __init__(self):    
        self.point = None
        self.selected_emotion = None

    def on_play(self):
        try:
            data, samplerate = sf.read("temp.wav", dtype='float32')
            play_obj = sd.play(data, samplerate)
            # play_obj.wait_done()  # optionnel : bloquer jusqu'à la fin
            #print(f"Lecture de {WAV_FILE}")
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier : {e}")

    def on_next(self):
        #print("Next")
        self.canvas.delete(self.point)
        self.point = None
        sd.stop()
        self.root.destroy()

    def convert_coordinates(self, x, y):
        center_x = CANVAS_SIZE / 2
        center_y = CANVAS_SIZE / 2
        dx = x - center_x
        dy = center_y - y  # Inverser l'axe y pour un angle correct
        r = math.sqrt(dx**2 + dy**2) / (CANVAS_SIZE / 2)  # Normalisé entre 0 et 1
        theta = math.atan2(dy, dx)  # Angle en radians
        return r, theta

    def on_click(self, event):
        x, y = event.x, event.y
        r, theta = self.convert_coordinates(x, y)
        emotion_vals = polar_to_emotion(r, theta)   
        #print(f"Émotion sélectionnée : r={r:.2f}, θ={math.degrees(theta):.2f}° -> {emotion_vals.__dict__}")
    
        # Si le point est dans la zone
        if r < 1 :
            if self.point is not None:
                self.canvas.delete(self.point)
            self.point = self.canvas.create_oval(
                x-POINT_RADIUS, y-POINT_RADIUS,
                x+POINT_RADIUS, y+POINT_RADIUS,
                fill="red", outline=""
            )
        self.selected_emotion = emotion_vals
    
    def loop(self):
        self.root = tk.Tk()
        
        self.root.title("Interface musicale")
        self.root.geometry(f"{WINDOW_SIZE}x{WINDOW_SIZE}")
        self.root.resizable(False, False)

        # Frame du haut
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=5)

        # Canvas
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack()
        self.canvas = tk.Canvas(canvas_frame, width=CANVAS_SIZE, height=CANVAS_SIZE)
        self.canvas.pack()

        # Charger l'image et l'adapter automatiquement au Canvas
        img = Image.open(IMAGE_PATH)

        img_resized = img.resize((CANVAS_SIZE, CANVAS_SIZE), Image.Resampling.LANCZOS)
        bg_image = ImageTk.PhotoImage(img_resized)

        # Centrer l'image sur le Canvas
        self.canvas.create_image(CANVAS_SIZE//2, CANVAS_SIZE//2, image=bg_image)

        self.canvas.bind("<Button-1>", self.on_click)

        # Frame du bas
        bottom_frame = tk.Frame(self.root, width=CANVAS_SIZE)
        bottom_frame.pack(pady=20)

        self.button_font = tkfont.Font(
            family="Helvetica",
            size=14,
            weight="bold"
        )

        play_button = tk.Button(bottom_frame, text="Play", width=30, height = 8, command=self.on_play, bg="#9BCEF8", font=self.button_font)
        play_button.pack(side="left")
        next_button = tk.Button(bottom_frame, text="Next", width=30, height = 8, command=self.on_next, bg="#9BCEF8", font=self.button_font)
        next_button.pack(side="right")
        
        self.root.mainloop()
        return self.selected_emotion
    
"""
a = input()
selected_emotion = a.loop()
print(f"selected_emotion: ({selected_emotion})")
"""

    

