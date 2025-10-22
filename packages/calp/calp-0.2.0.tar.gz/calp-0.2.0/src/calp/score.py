import datetime
import json
from importlib.resources import files
from pathlib import Path
from time import perf_counter
from zoneinfo import ZoneInfo

import arcade

import calp.assets.images
from calp.constants import (
    DARKER_BLUE,
    GAME_DURATION_SECONDS,
    LIGHT_BLUE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)

SCORE_HEIGHT = 100
SCORE_MARGIN = 20


class ScoreManager:
    def __init__(self):
        self._score = 0
        self._start_time = perf_counter()
        self._previous_time = -1

    def setup(self):
        self._score = 0
        self._start_time = perf_counter()
        self._shape_list = arcade.shape_list.ShapeElementList()
        self._shape_list.clear()
        self._shape_list.append(
            arcade.shape_list.create_rectangle_filled(
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT - SCORE_HEIGHT / 2,
                SCREEN_WIDTH,
                SCORE_HEIGHT,
                LIGHT_BLUE,
            )
        )

        self._sprite_list = arcade.SpriteList()
        sprite = arcade.Sprite(files(calp.assets.images) / "logo-full.png", scale=0.5)
        sprite.center_x = SCREEN_WIDTH / 2
        sprite.center_y = SCREEN_HEIGHT - SCORE_HEIGHT / 2
        self._sprite_list.append(sprite)

        self._setup_text()

    def _setup_text(self):
        self._score_text = arcade.Text(
            f"Score : {self.score}",
            x=SCORE_MARGIN,
            y=SCREEN_HEIGHT - SCORE_HEIGHT / 2,
            anchor_y="center",
            color=DARKER_BLUE,
            font_size=22,
            font_name="Fira Code",
        )
        self._time_text = arcade.Text(
            f"Temps restant : {self.time_left}",
            x=SCREEN_WIDTH - SCORE_MARGIN,
            y=SCREEN_HEIGHT - SCORE_HEIGHT / 2,
            anchor_x="right",
            anchor_y="center",
            color=DARKER_BLUE,
            font_size=22,
            font_name="Fira Code",
        )

    def draw(self):
        self._shape_list.draw()
        self._sprite_list.draw()
        self._score_text.draw()
        self._update_time()
        self._time_text.draw()

    def _update_time(self):
        if (remaining_time := self.time_left) != self._previous_time:
            self._previous_time = remaining_time
            self._setup_text()

    def good_icon_caught(self):
        if self.time_left:
            self._score += 3
            self._setup_text()

    def enemy_icon_caught(self):
        if self.time_left:
            self._score -= 1
            self._setup_text()

    @property
    def score(self):
        return self._score

    @property
    def time_left(self):
        return max(0, GAME_DURATION_SECONDS - int(perf_counter() - self._start_time))


class HighScoresManager:
    STORAGE_PATH = Path.home() / ".calp_high_scores.json"

    def __init__(self):
        if self.STORAGE_PATH.exists():
            self.high_scores = json.loads(self.STORAGE_PATH.read_text(encoding="utf-8"))
        else:
            self.high_scores = []
        self.current_score = 0
        self.current_date = datetime.datetime.now(tz=ZoneInfo("Europe/Paris")).strftime(
            "%Y-%m-%d %H:%M:%S",
        )

    def add_score(self, score):
        self.current_score = score
        self.current_date = datetime.datetime.now(tz=ZoneInfo("Europe/Paris")).strftime(
            "%d/%m/%Y %H:%M:%S",
        )
        self.high_scores.append([self.current_score, self.current_date])
        self.high_scores.sort(reverse=True)
        self.high_scores = self.high_scores[:10]
        self.STORAGE_PATH.write_text(json.dumps(self.high_scores), encoding="utf-8")


score_manager = ScoreManager()
high_scores_manager = HighScoresManager()
