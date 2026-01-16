class Note:
    def __init__(self, pitch, intensity, duration, slide=False):
        self.pitch = pitch
        self.intensity = intensity
        self.duration = duration
        self.slide = slide