from pathlib import Path
import os

WIDTH, HEIGHT = 1100, 760
FPS = 60
ROUND_SIZE = 10
BACKGROUND = (18, 24, 44)
PANEL = (31, 41, 65)
TEXT = (239, 244, 255)
MUTED = (168, 185, 211)
ACCENT = (96, 211, 190)
ERROR = (255, 135, 145)
DATA_DIR = Path(os.environ.get("ACADEMY_DATA_DIR", Path(os.environ.get("LOCALAPPDATA", Path.home())) / "MultiplicationAcademy"))
