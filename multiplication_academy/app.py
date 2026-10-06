import argparse
import os
from pathlib import Path
import pygame
from .config import BACKGROUND, DATA_DIR, FPS, HEIGHT, WIDTH, MUTED
from .core.progress import Profile, ProgressStore
from .core.round import Round
from .screens.views import VIEWS
from .utils.ui import UI

class Academy:
    def __init__(self, data_dir: Path = DATA_DIR):
        pygame.init()
        pygame.display.set_caption("Академия умножения")
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.ui = UI(self.surface)
        self.clock = pygame.time.Clock()
        self.store = ProgressStore(data_dir)
        self.profile: Profile | None = None
        self.round: Round | None = None
        self.screen = "profiles"
        self.name_input = ""
        self.notice = self.store.warning
        self.profile_page = 0
        self.last_correct = False
        self.running = True
        pygame.key.start_text_input()

    def navigate(self, screen: str) -> None:
        self.screen = screen
        self.ui.buttons.clear()

    def page(self, direction: int) -> None:
        self.profile_page = max(0, self.profile_page + direction)

    def create_profile(self) -> None:
        try:
            self.select_profile(self.store.create_profile(self.name_input))
            self.name_input = ""
            self.notice = ""
        except ValueError as exc:
            self.notice = str(exc)

    def select_profile(self, profile: Profile) -> None:
        self.profile = profile
        self.navigate("menu")

    def start_round(self, table: int) -> None:
        self.round = Round(self.profile, table)
        self.round.next_question()
        self.store.save()
        self.navigate("game")

    def answer(self, value: int) -> None:
        if self.round.answered:
            return
        self.last_correct = self.round.answer(value)
        self.store.save()
        self.ui.buttons.clear()

    def advance(self) -> None:
        if not self.round.answered:
            return
        if self.round.finished:
            self.navigate("result")
        else:
            self.round.next_question()
            self.store.save()
            self.ui.buttons.clear()

    def handle(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.ui.click(event.pos)
        elif event.type == pygame.TEXTINPUT and self.screen == "profiles":
            self.name_input = (self.name_input + ''.join(c for c in event.text if c.isprintable()))[:24]
        elif event.type == pygame.KEYDOWN:
            if self.screen == "profiles":
                if event.key == pygame.K_BACKSPACE:
                    self.name_input = self.name_input[:-1]
                elif event.key == pygame.K_RETURN:
                    self.create_profile()
            elif self.screen == "game":
                if self.round.answered and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.advance()
                elif not self.round.answered and event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    self.answer(self.round.options[event.key - pygame.K_1])
            elif event.key == pygame.K_ESCAPE:
                self.navigate("menu" if self.profile else "profiles")

    def frame(self) -> None:
        for event in pygame.event.get():
            self.handle(event)
        self.surface.fill(BACKGROUND)
        self.ui.buttons.clear()
        self.ui.text("АКАДЕМИЯ УМНОЖЕНИЯ", 70, 45, 34)
        self.ui.text("Учись • пробуй • побеждай", 70, 95, 20, MUTED)
        VIEWS[self.screen](self)
        pygame.display.flip()
        self.clock.tick(FPS)

    def run(self) -> None:
        try:
            while self.running:
                self.frame()
        finally:
            self.store.save()
            pygame.quit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Академия умножения")
    parser.add_argument("--smoke", action="store_true", help="Проверить экраны и игровой цикл без окна")
    args = parser.parse_args()
    if args.smoke:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directory:
            app = Academy(Path(directory))
            app.frame()
            pygame.event.post(pygame.event.Event(pygame.TEXTINPUT, text="Тест"))
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
            app.frame()
            assert app.screen == "menu"
            app.start_round(7)
            for _ in range(10):
                app.frame()
                index = app.round.options.index(app.round.question.answer)
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1 + index))
                app.frame()
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
                app.frame()
            assert app.screen == "result" and app.round.score.correct == 10
            app.navigate("progress")
            app.frame()
            app.start_round(3)
            for _ in range(3):
                app.answer(next(v for v in app.round.options if v != app.round.question.answer))
                app.frame()
                app.advance()
            assert app.screen == "result" and app.round.score.lives == 0
            app.frame()
            loaded = ProgressStore(Path(directory))
            assert loaded.profiles[0].asked == 13
            app.running = False
            app.run()
            print("SMOKE OK: profiles, menu, 10 answers, feedback, result, progress, 3 lives, JSON")
    else:
        Academy().run()
