import random
from .progress import Profile
from .questions import Question, table_questions

class AdaptiveSelector:
    def __init__(self, profile: Profile, rng: random.Random):
        self.profile = profile
        self.rng = rng

    def choose(self, table: int) -> Question:
        p = self.profile
        available = [q for q in table_questions(table) if q.key != p.last_key]
        due = [q for q in available if q.key in p.pending and p.pending[q.key] <= p.asked + 1]
        if due:
            selected = min(due, key=lambda q: p.pending[q.key])
            del p.pending[selected.key]
            return selected
        available = [q for q in available if q.key not in p.pending]
        # At most three mistakes per round; normally several candidates remain.
        if not available:
            available = [q for q in table_questions(table) if q.key != p.last_key]
        weights = []
        for q in available:
            stat = p.example(q.key)
            weight = 4.0 if stat.shown == 0 else .35 if stat.mastered else 1.5 + 5 * stat.errors / stat.shown
            weights.append(weight)
        return self.rng.choices(available, weights=weights, k=1)[0]

    def schedule_mistake(self, key: str) -> None:
        # Current question is N; 3–5 OTHER questions, then repeat at N+4..N+6.
        self.profile.pending[key] = self.profile.asked + self.rng.randint(4, 6)
