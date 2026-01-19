import os


class ScoreManager:
    def __init__(self, filepath="highscore.txt"):
        self.filepath = filepath
        self.high_score = self.load_score()

    def load_score(self):
        if not os.path.exists(self.filepath):
            return 0
        try:
            with open(self.filepath, "r") as f:
                return int(f.read())
        except (ValueError, IOError):
            return 0

    def save_score(self):
        try:
            with open(self.filepath, "w") as f:
                f.write(str(self.high_score))
        except IOError:
            print("Error")

    def check_and_update(self, current_score):
        if current_score > self.high_score:
            self.high_score = current_score
            self.save_score()
            return True
        return False

    def get_high_score(self):
        return self.high_score
