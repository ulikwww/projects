from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import uuid

@dataclass
class ExampleStats:
    shown: int = 0
    correct: int = 0
    errors: int = 0
    streak: int = 0
    last_shown: str | None = None

    @property
    def mastered(self) -> bool:
        return self.shown >= 5 and self.correct / self.shown >= .8 and self.streak >= 3

@dataclass
class Profile:
    id: str
    name: str
    stats: dict[str, ExampleStats]
    asked: int
    pending: dict[str, int]
    last_key: str | None = None

    def example(self, key: str) -> ExampleStats:
        return self.stats.setdefault(key, ExampleStats())

    def mark_shown(self, key: str) -> None:
        self.asked += 1
        self.last_key = key
        stat = self.example(key)
        stat.shown += 1
        stat.last_shown = datetime.now(timezone.utc).isoformat()

    def mark_answer(self, key: str, correct: bool) -> None:
        stat = self.example(key)
        if correct:
            stat.correct += 1
            stat.streak += 1
        else:
            stat.errors += 1
            stat.streak = 0

class ProgressStore:
    def __init__(self, directory: Path):
        directory.mkdir(parents=True, exist_ok=True)
        self.path = directory / "progress.json"
        self.profiles: list[Profile] = []
        self.warning = ""
        if self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                if raw.get("version") != 1 or not isinstance(raw["profiles"], list):
                    raise ValueError("Unsupported save")
                for p in raw["profiles"]:
                    if not isinstance(p["name"], str) or not p["name"].strip() or not isinstance(p["id"], str):
                        raise ValueError("Invalid profile")
                    stats = {}
                    for key, values in p["stats"].items():
                        a, b = map(int, key.split("x"))
                        if a not in range(2, 10) or b not in range(1, 11):
                            raise ValueError("Invalid example")
                        stat = ExampleStats(**values)
                        if any(type(n) is not int or n < 0 for n in (stat.shown, stat.correct, stat.errors, stat.streak)):
                            raise ValueError("Invalid statistics")
                        if stat.correct + stat.errors > stat.shown or stat.streak > stat.correct:
                            raise ValueError("Invalid statistics")
                        if stat.last_shown is not None:
                            datetime.fromisoformat(stat.last_shown)
                        stats[key] = stat
                    asked = p["asked"]
                    pending = p["pending"]
                    if type(asked) is not int or asked < 0 or not isinstance(pending, dict):
                        raise ValueError("Invalid schedule")
                    for key, due in pending.items():
                        a, b = map(int, key.split("x"))
                        if a not in range(2, 10) or b not in range(1, 11) or type(due) is not int or due < 0:
                            raise ValueError("Invalid schedule")
                    self.profiles.append(Profile(p["id"], p["name"], stats, asked, pending, p.get("last_key")))
            except (ValueError, TypeError, KeyError, AttributeError):
                self.profiles = []
                backup = self.path.with_name(f"progress-damaged-{uuid.uuid4().hex[:8]}.json")
                self.path.replace(backup)
                self.warning = "Повреждённое сохранение сохранено в резервной копии."
        self.save()

    def create_profile(self, name: str) -> Profile:
        name = name.strip()[:24]
        if not name:
            raise ValueError("Введите имя")
        profile = Profile(uuid.uuid4().hex, name, {}, 0, {})
        self.profiles.append(profile)
        self.save()
        return profile

    def save(self) -> None:
        data = {"version": 1, "profiles": [asdict(p) for p in self.profiles]}
        temp = self.path.with_suffix(".tmp")
        with temp.open("w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        temp.replace(self.path)
