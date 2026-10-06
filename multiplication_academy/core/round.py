import random
from .adaptive import AdaptiveSelector
from .progress import Profile
from .questions import Question
from .scoring import Score
from ..config import ROUND_SIZE

class Round:
    def __init__(self, profile: Profile, table: int, rng: random.Random | None = None):
        self.profile = profile
        self.table = table
        self.rng = rng or random.Random()
        self.selector = AdaptiveSelector(profile, self.rng)
        self.score = Score()
        self.question: Question | None = None
        self.options: list[int] = []
        self.answered = True
        self.count = 0

    @property
    def finished(self) -> bool:
        return self.score.lives == 0 or self.score.correct + self.score.errors >= ROUND_SIZE

    def next_question(self) -> None:
        if not self.answered or self.finished:
            return
        self.question = self.selector.choose(self.table)
        self.options = self.question.options(self.rng)
        self.profile.mark_shown(self.question.key)
        self.count += 1
        self.answered = False

    def answer(self, value: int) -> bool:
        if self.answered or self.question is None:
            raise ValueError("Question already answered")
        correct = value == self.question.answer
        self.profile.mark_answer(self.question.key, correct)
        self.score.answer(correct)
        if not correct:
            self.selector.schedule_mistake(self.question.key)
        self.answered = True
        return correct
