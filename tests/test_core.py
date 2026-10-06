import json
from pathlib import Path
import random
from tempfile import TemporaryDirectory
import unittest

from multiplication_academy.core.adaptive import AdaptiveSelector
from multiplication_academy.core.progress import ExampleStats, Profile, ProgressStore
from multiplication_academy.core.questions import table_questions
from multiplication_academy.core.round import Round


class AcademyTests(unittest.TestCase):
    def profile(self) -> Profile:
        return Profile('test', 'Ученик', {}, 0, {})

    def test_options_all_tables(self) -> None:
        rng = random.Random(8)
        for table in range(2, 10):
            for q in table_questions(table):
                for _ in range(20):
                    options = q.options(rng)
                    self.assertEqual(len(set(options)), 4)
                    self.assertIn(q.answer, options)
                    self.assertTrue(all(n > 0 for n in options))

    def test_mastery(self) -> None:
        self.assertTrue(ExampleStats(5, 4, 1, 3).mastered)
        self.assertFalse(ExampleStats(4, 4, 0, 4).mastered)
        self.assertFalse(ExampleStats(6, 4, 2, 3).mastered)
        self.assertFalse(ExampleStats(5, 4, 1, 2).mastered)

    def test_delayed_repeat_across_rounds(self) -> None:
        for seed in range(50):
            p = self.profile()
            r = Round(p, 6, random.Random(seed))
            for _ in range(9):
                r.next_question()
                r.answer(r.question.answer)
            r.next_question()
            failed_key = r.question.key
            r.answer(-1)
            failed_at = p.asked
            due = p.pending[failed_key]
            self.assertIn(due - failed_at, (4, 5, 6))
            r = Round(p, 6, random.Random(seed + 100))
            while p.asked < due:
                previous = p.last_key
                r.next_question()
                self.assertNotEqual(previous, r.question.key)
                if p.asked < due:
                    self.assertNotEqual(failed_key, r.question.key)
                else:
                    self.assertEqual(failed_key, r.question.key)
                r.answer(r.question.answer)

    def test_adaptive_distribution(self) -> None:
        p = self.profile()
        for q in table_questions(2):
            p.stats[q.key] = ExampleStats(10, 10, 0, 10)
        p.stats['2x1'] = ExampleStats()
        p.stats['2x2'] = ExampleStats(10, 3, 7, 0)
        selector = AdaptiveSelector(p, random.Random(123))
        counts = {q.key: 0 for q in table_questions(2)}
        for _ in range(6000):
            q = selector.choose(2)
            self.assertNotEqual(q.key, p.last_key)
            p.last_key = q.key
            counts[q.key] += 1
        self.assertGreater(counts['2x1'], counts['2x3'] * 3)
        self.assertGreater(counts['2x2'], counts['2x3'] * 3)

    def test_profile_save_load(self) -> None:
        with TemporaryDirectory() as folder:
            store = ProgressStore(Path(folder))
            one = store.create_profile('Аня')
            two = store.create_profile('Борис')
            one.mark_shown('3x4')
            one.mark_answer('3x4', False)
            one.pending['3x4'] = 6
            store.save()
            loaded = ProgressStore(Path(folder))
            self.assertEqual(loaded.profiles[0], one)
            self.assertEqual(loaded.profiles[1], two)
            self.assertEqual(loaded.profiles[0].stats['3x4'].errors, 1)

    def test_corrupt_saves(self) -> None:
        for content in ['{broken', '[]', '{"version":99,"profiles":[]}', '{"version":1,"profiles":[{}]}']:
            with TemporaryDirectory() as folder:
                path = Path(folder) / 'progress.json'
                path.write_text(content, encoding='utf-8')
                store = ProgressStore(Path(folder))
                self.assertEqual(store.profiles, [])
                self.assertTrue(store.warning)
                self.assertEqual(len(list(Path(folder).glob('progress-damaged-*.json'))), 1)
                self.assertEqual(json.loads(path.read_text())['version'], 1)

    def test_round_lives_and_single_answer(self) -> None:
        r = Round(self.profile(), 9, random.Random(3))
        for _ in range(3):
            r.next_question()
            r.answer(-1)
            with self.assertRaises(ValueError):
                r.answer(-1)
        self.assertTrue(r.finished)
        self.assertEqual(r.score.lives, 0)
        self.assertEqual(r.score.percentage, 0)
        r.next_question()
        self.assertEqual(r.count, 3)


if __name__ == '__main__':
    unittest.main()
