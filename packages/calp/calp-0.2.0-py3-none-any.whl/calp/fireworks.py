from importlib.resources import files
from pathlib import Path
from time import perf_counter

from arcade.experimental.shadertoy import Shadertoy

import calp.assets
from calp.constants import SCREEN_HEIGHT, SCREEN_WIDTH

ANIMATION_DURATION = 0.9  # seconds


class Firework:
    def __init__(self, position):
        self.shadertoy = Shadertoy(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            main_source=Path(files(calp.assets) / "firework.glsl").read_text(
                encoding="utf-8"
            ),
        )
        self.shadertoy.program["explosionPos"] = position
        self.position = position
        self.start_time = perf_counter()

    def render(self):
        self.shadertoy.render(time=perf_counter() - self.start_time)

    def finished(self):
        return perf_counter() - self.start_time > ANIMATION_DURATION
