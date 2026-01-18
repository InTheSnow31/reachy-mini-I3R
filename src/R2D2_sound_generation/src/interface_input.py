import tkinter as tk
import tkinter.font as tkfont
from PIL import Image, ImageTk
import math
import sounddevice as sd
import soundfile as sf
from emotion import polar_to_emotion
import sys

WINDOW_SIZE = 800
CANVAS_SIZE = 700
POINT_RADIUS = 5
WAV_FILE = "temp/temp.wav"  # fichier à jouer

class input:
    def __init__(self, EMOTION_MODEL):
        self.EMOTION_MODEL = EMOTION_MODEL
        self.selected_emotion = None
        self.on_play()

    def on_play(self):
        try:
            data, samplerate = sf.read("temp.wav", dtype='float32')
            sd.play(data, samplerate)
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier : {e}")
            
    def on_next(self):
        if self.EMOTION_MODEL["system"] == "wheel":
            self.canvas.delete(self.point)
        else :
            self.selected_emotion = [var.get() for var in self.sliders]
        sd.stop()
        self.root.destroy()

    def convert_coordinates(self, x, y):
        center_x, center_y = CANVAS_SIZE / 2, CANVAS_SIZE / 2
        dx, dy = x - center_x, center_y - y
        r = math.sqrt(dx**2 + dy**2) / (CANVAS_SIZE / 2)  
        theta = math.atan2(dy, dx)  
        return r, theta

    def on_click_wheel(self, event):
        x, y = event.x, event.y
        r, theta = self.convert_coordinates(x, y)
        emotion_vals = polar_to_emotion(self.EMOTION_MODEL, r, theta)
    
        # check if the point is inside the wheel
        if r < 1 :
            if self.point is not None:
                self.canvas.delete(self.point)
            self.point = self.canvas.create_oval(
                x-POINT_RADIUS, y-POINT_RADIUS,
                x+POINT_RADIUS, y+POINT_RADIUS,
                fill="red", outline=""
            )

        # Enable "next" validation button
        self.next_button.config(state="normal")
        self.selected_emotion = emotion_vals
    
    def close_all(self):
        self.root.destroy()
        sd.stop()
        sys.exit()

    def initialise_wheel(self):
        # Variables
        self.point = None

        # Canvas
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack()
        self.canvas = tk.Canvas(canvas_frame, width=CANVAS_SIZE, height=CANVAS_SIZE)
        self.canvas.pack()

        # Charger l'image et l'adapter automatiquement au Canvas
        img = Image.open(self.EMOTION_MODEL["wheel_path"])

        img_resized = img.resize((CANVAS_SIZE, CANVAS_SIZE), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(img_resized)

        # Centrer l'image sur le Canvas
        self.canvas.create_image(CANVAS_SIZE//2, CANVAS_SIZE//2, image=self.bg_image)
        self.canvas.bind("<Button-1>", self.on_click_wheel)
    
    def initialise_bars(self):
        self.sliders = []

        bars_frame = tk.Frame(self.root)
        bars_frame.pack(pady=20)

        emotion_axes = self.EMOTION_MODEL["emotion_names"]

        for left_label, right_label in emotion_axes:
            col = tk.Frame(bars_frame)
            col.pack(side="left", padx=15)

            var = tk.DoubleVar(value=0.5)

            slider = tk.Scale(
                col,
                variable=var,
                from_=1.0,
                to=0.0,
                resolution=0.01,
                orient="vertical",
                length=500,
                width=22
            )
            slider.pack()

            label_top = tk.Label(
                col,
                text=right_label,
                font=("Helvetica", 11, "bold")
            )
            label_top.pack(pady=(5, 0))

            label_bottom = tk.Label(
                col,
                text=left_label,
                font=("Helvetica", 11, "bold")
            )
            label_bottom.pack(pady=(0, 5))

            self.sliders.append(var)



    def loop(self):
        self.root = tk.Tk()
        
        self.root.title("Interface musicale")
        self.root.geometry(f"{WINDOW_SIZE}x{WINDOW_SIZE}")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.close_all)

        # Frame du haut
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=5)
        if self.EMOTION_MODEL["system"] == "wheel":
            self.initialise_wheel()
        elif self.EMOTION_MODEL["system"] == "bars":
            self.initialise_bars()


        # Frame du bas
        bottom_frame = tk.Frame(self.root, width=CANVAS_SIZE)
        bottom_frame.pack(pady=20)

        self.button_font = tkfont.Font(family="Helvetica", size=14, weight="bold")

        play_button = tk.Button(bottom_frame, text="Play", width=30, height = 8, command=self.on_play, bg="#9BCEF8", font=self.button_font)
        play_button.pack(side="left")
        self.next_button = tk.Button(bottom_frame, text="Next", width=30, height = 8, command=self.on_next, bg="#9BCEF8", font=self.button_font)
        self.next_button.pack(side="right")

        # Protection to None emotion
        if self.EMOTION_MODEL["system"] == "wheel":
            self.next_button.config(state="disabled")
        else :
            self.selected_emotion = [var.get() for var in self.sliders]
        
        self.root.mainloop()

        return self.selected_emotion

    

