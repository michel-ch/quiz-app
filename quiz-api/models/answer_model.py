class Answer:
    def __init__(self, text: str, is_correct: bool, latitude: float = None, longitude: float = None):
        self.text = text
        self.is_correct = is_correct
        self.latitude = latitude
        self.longitude = longitude