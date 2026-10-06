from dataclasses import dataclass
import random

@dataclass(frozen=True)
class Question:
    table: int
    factor: int

    @property
    def key(self) -> str:
        return f"{self.table}x{self.factor}"

    @property
    def answer(self) -> int:
        return self.table * self.factor

    def options(self, rng: random.Random) -> list[int]:
        candidates = {self.answer + d for d in (-self.table, self.table, -self.factor, self.factor, -1, 1, -2, 2)}
        candidates = {x for x in candidates if x > 0 and x != self.answer}
        wrong = rng.sample(sorted(candidates), 3)
        result = [self.answer, *wrong]
        rng.shuffle(result)
        return result


def table_questions(table: int) -> list[Question]:
    if table not in range(2, 10):
        raise ValueError("Table must be between 2 and 9")
    return [Question(table, factor) for factor in range(1, 11)]
