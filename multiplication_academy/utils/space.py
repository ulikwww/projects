"""A small animated mission scene drawn entirely with Pygame primitives."""
import math
import random
import pygame
from ..config import ACCENT, MUTED
from .effects import Effects
from .ui import UI

PLANETS = ['Бирюза', 'Янтарь', 'Аврора', 'Орион', 'Лагуна', 'Комета', 'Вега', 'Нова']
COLORS = [(79, 206, 183), (251, 190, 96), (175, 132, 246), (114, 169, 253), (83, 205, 220), (247, 148, 177), (196, 218, 129), (228, 179, 252)]


class SpaceScene:
    def __init__(self, effects: Effects) -> None:
        self.effects = effects
        rng = random.Random(21)
        self.stars = [(rng.randrange(1100), rng.randrange(760), rng.uniform(8, 30), rng.choice([1, 1, 2])) for _ in range(85)]
        self.travel = 0.0
        self.target = 0.0

    def reset(self) -> None:
        self.travel = self.target = 0.0

    def update(self, dt: float) -> None:
        self.travel += (self.target - self.travel) * min(1, dt * 4)

    def background(self, surface: pygame.Surface, boost: bool = False) -> None:
        t = self.effects.elapsed
        for x, y, speed, size in self.stars:
            position = (int((x - t * speed * (3 if boost else 1)) % 1100), y)
            pygame.draw.circle(surface, (65 + size * 30, 80 + size * 30, 115 + size * 35), position, size)
            if boost:
                pygame.draw.line(surface, (61, 89, 128), position, (position[0] + 16, y), size)

    def ship(self, surface: pygame.Surface, x: int, y: int, boost: bool = False) -> None:
        t = self.effects.elapsed
        flame = 22 + int(8 * math.sin(t * 24)) + (20 if boost else 0)
        pygame.draw.polygon(surface, (255, 184, 91), [(x - 30, y - 9), (x - 30 - flame, y), (x - 30, y + 9)])
        pygame.draw.polygon(surface, ACCENT, [(x - 33, y - 20), (x - 2, y - 13), (x + 5, y), (x - 25, y + 29)])
        pygame.draw.polygon(surface, (230, 239, 255), [(x - 34, y - 13), (x + 28, y), (x - 34, y + 13)])
        pygame.draw.circle(surface, (41, 76, 114), (x - 4, y), 9)
        pygame.draw.circle(surface, (114, 217, 248), (x - 3, y - 1), 5)

    def mission(self, ui: UI, table: int, lives: int, streak: int) -> None:
        ui.panel((640, 145, 390, 285))
        ui.text('ЦЕЛЬ: ' + PLANETS[table - 2].upper(), 660, 164, 20, MUTED)
        surface = ui.surface
        color = COLORS[table - 2]
        pygame.draw.circle(surface, (52, 59, 89), (968, 274), 43)
        pygame.draw.circle(surface, color, (968, 274), 34)
        pygame.draw.circle(surface, tuple(int(c * .8) for c in color), (978, 282), 15)
        pygame.draw.ellipse(surface, (207, 216, 246), (918, 263, 100, 25), 2)
        shake = int(math.sin(self.effects.elapsed * 65) * 5 * self.effects.flash) if not self.effects.correct else 0
        x = 728 + int(self.travel * 190) + shake
        y = 273 + int(math.sin(self.effects.elapsed * 3) * 6)
        boost = streak >= 3
        self.ship(surface, x, y, boost)
        for i in range(lives):
            pygame.draw.arc(surface, ACCENT, (x - 46 - i * 4, y - 34 - i * 4, 82 + i * 8, 68 + i * 8), -.8, .8, 2)
        ui.text('ГИПЕРДРАЙВ!' if boost else 'Заряди корабль ответами', 660, 334, 22, ACCENT if boost else MUTED)
        pygame.draw.rect(surface, (50, 62, 91), (660, 382, 350, 12), border_radius=6)
        width = int(350 * self.travel)
        if width:
            pygame.draw.rect(surface, ACCENT, (660, 382, width, 12), border_radius=6)

    @staticmethod
    def medal(surface: pygame.Surface, x: int, y: int, active: bool) -> None:
        points = []
        for i in range(10):
            angle = -math.pi / 2 + i * math.pi / 5
            radius = 35 if i % 2 == 0 else 16
            points.append((x + math.cos(angle) * radius, y + math.sin(angle) * radius))
        pygame.draw.polygon(surface, (255, 206, 109) if active else (64, 75, 103), points)
