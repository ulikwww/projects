"""Procedural animation and sound; no downloaded assets or gameplay randomness."""
from array import array
from dataclasses import dataclass
import math
import random
import pygame


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    color: tuple[int, int, int]


class Effects:
    def __init__(self) -> None:
        self.rng = random.Random()
        self.particles: list[Particle] = []
        self.elapsed = 0.0
        self.flash = 0.0
        self.correct = True
        self.muted = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        mixer = pygame.mixer.get_init()
        if mixer and mixer[1] == -16:
            rate, _, channels = mixer
            for name, notes in {'correct': [523, 659, 784], 'error': [294, 220], 'boost': [523, 659, 784, 1047]}.items():
                samples = array('h')
                for frequency in notes:
                    length = int(rate * .085)
                    for index in range(length):
                        envelope = math.sin(math.pi * index / length) ** 2
                        sample = int(2200 * envelope * math.sin(2 * math.pi * frequency * index / rate))
                        samples.extend([sample] * channels)
                self.sounds[name] = pygame.mixer.Sound(buffer=samples)

    def burst(self, x: int, y: int, color: tuple[int, int, int], count: int = 36) -> None:
        for _ in range(count):
            angle = self.rng.uniform(0, math.tau)
            speed = self.rng.uniform(70, 270)
            self.particles.append(Particle(x, y, math.cos(angle) * speed, math.sin(angle) * speed, self.rng.uniform(.5, 1.3), color))

    def feedback(self, correct: bool, streak: int) -> None:
        self.correct = correct
        self.flash = .65
        color = (96, 235, 203) if correct else (255, 145, 160)
        self.burst(790, 270, color, 55 if correct else 16)
        name = 'boost' if correct and streak >= 3 else 'correct' if correct else 'error'
        if not self.muted and name in self.sounds:
            self.sounds[name].play()

    def update(self, dt: float) -> None:
        self.elapsed += dt
        self.flash = max(0.0, self.flash - dt)
        for particle in self.particles:
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            particle.vy += 95 * dt
            particle.life -= dt
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surface: pygame.Surface) -> None:
        for particle in self.particles:
            pygame.draw.circle(surface, particle.color, (int(particle.x), int(particle.y)), max(1, int(4 * min(1, particle.life))))
