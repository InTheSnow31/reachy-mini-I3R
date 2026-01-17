class Note:
    def __init__(self, pitch, intensity, duration, slide=False):
        self.pitch = pitch
        self.intensity = intensity
        self.duration = duration
        self.slide = slide
    
    def __str__(self):
        return "Pitch : " + str(self.pitch) + " | Intensity : " + str(self.intensity) + " | duration : " + str(self.duration) + " | Sliding ? " + str(self.slide)