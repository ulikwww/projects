from dataclasses import dataclass

@dataclass
class Score:
    correct: int = 0
    errors: int = 0
    points: int = 0
    streak: int = 0
    best_streak: int = 0
    lives: int = 3

    def answer(self, correct: bool) -> None:
        if correct:
            self.correct += 1
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
            self.points += 100 + min(self.streak - 1, 5) * 20
        else:
            self.errors += 1
            self.streak = 0
            self.lives -= 1

    @property
    def percentage(self) -> int:
        total = self.correct + self.errors
        return round(100 * self.correct / total) if total else 0
