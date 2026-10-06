from collections.abc import Callable
import pygame
from ..config import ACCENT, MUTED, PANEL, TEXT

class UI:
    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self.buttons: list[tuple[pygame.Rect, Callable[[], None]]] = []
        self.fonts: dict[int, pygame.font.Font] = {}
        self.font_path = pygame.font.match_font("segoeui,dejavusans,arial")

    def font(self, size: int) -> pygame.font.Font:
        if size not in self.fonts:
            self.fonts[size] = pygame.font.Font(self.font_path, size)
        return self.fonts[size]

    def text(self, text: str, x: int, y: int, size: int = 24, color: tuple[int, int, int] = TEXT) -> None:
        font = self.font(size)
        self.surface.blit(font.render(text, True, color), (x, y))

    def panel(self, rect: tuple[int, int, int, int]) -> None:
        pygame.draw.rect(self.surface, PANEL, rect, border_radius=20)

    def button(self, text: str, rect: tuple[int, int, int, int], action: Callable[[], None], accent: bool = False) -> None:
        box = pygame.Rect(rect)
        hovered = box.collidepoint(pygame.mouse.get_pos())
        color = ACCENT if accent else (51, 67, 99) if hovered else PANEL
        pygame.draw.rect(self.surface, color, box, border_radius=15)
        font = self.font(24)
        label = font.render(text, True, (18, 24, 44) if accent else TEXT)
        self.surface.blit(label, label.get_rect(center=box.center))
        self.buttons.append((box, action))

    def click(self, position: tuple[int, int]) -> None:
        for rect, action in self.buttons:
            if rect.collidepoint(position):
                action()
                return
