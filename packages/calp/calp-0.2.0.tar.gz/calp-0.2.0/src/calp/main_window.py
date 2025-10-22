import math
from importlib.resources import files
from pathlib import Path
from time import perf_counter

import arcade
import pyglet

import calp.assets.images
import calp.assets.sounds
from calp.calamar import Calamar
from calp.constants import (
    DARK_BLUE,
    DARKER_BLUE,
    LIGHT_BLUE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from calp.icon import IconList
from calp.score import high_scores_manager, score_manager


class HighScoresView(arcade.View):
    def __init__(self):
        super().__init__()
        self.title = arcade.Text(
            "High Scores",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 100,
            DARKER_BLUE,
            font_size=50,
            anchor_x="center",
            font_name="Fira Code",
        )

        self._sprite_list = arcade.SpriteList()
        sprite = arcade.Sprite(
            files(calp.assets.images) / "blog_calamars_et_python.png", scale=0.4
        )
        sprite.center_x = SCREEN_WIDTH - 20 - sprite.width / 2
        sprite.center_y = SCREEN_HEIGHT / 2
        self._sprite_list.append(sprite)

        self.learn_this = arcade.Text(
            "Apprenez à coder ce jeu sur www.lecalamar.fr",
            sprite.center_x,
            sprite.center_y - sprite.height / 2 - 30,
            DARKER_BLUE,
            font_size=16,
            anchor_x="center",
            font_name="Fira Code",
            multiline=True,
            align="center",
            width=int(sprite.width),
        )

    def on_show_view(self):
        self.window.background_color = LIGHT_BLUE

    def on_draw(self):
        self.clear()
        self._sprite_list.draw()
        self.title.draw()
        self.learn_this.draw()

        text = arcade.Text(
            f"Score de cette partie : {high_scores_manager.current_score}",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 200,
            DARKER_BLUE,
            font_size=30,
            anchor_x="center",
            font_name="Fira Code",
        )
        text.draw()

        for index, (score, date) in enumerate(high_scores_manager.high_scores, start=1):
            text = arcade.Text(
                f"{index:2}) {score:3} points - {date}",
                20,
                SCREEN_HEIGHT - 250 - index * 40,
                DARKER_BLUE,
                font_size=22,
                font_name="Fira Code",
            )
            text.draw()

    def on_key_press(self, key, _modifiers):
        if key in {arcade.key.ENTER, arcade.key.SPACE, arcade.key.ESCAPE}:
            self.window.show_view(GameView())

    def on_mouse_press(self, _x, _y, button, _modifiers):
        if button == arcade.MOUSE_BUTTON_MIDDLE:
            self.window.show_view(GameView())


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.calamar = Calamar()
        self.icons = IconList()

        self.lines_shape_list = arcade.shape_list.ShapeElementList()

        self.setup()

    def on_show_view(self):
        self.window.background_color = LIGHT_BLUE

    def setup(self):  # called once at startup, or at reset
        self.calamar.setup()
        self.icons.clear()
        self.create_background()
        score_manager.setup()

    def create_background(self):
        self.lines_shape_list.clear()

        points = []
        for y in range(-40, SCREEN_HEIGHT + 40, 30):
            points.append((0, y + 20 * math.sin(perf_counter() + 2)))  # noqa: FURB113, extend is better than 2 appends
            points.append((SCREEN_WIDTH, y + 30 + 40 * math.sin(perf_counter())))

        self.lines_shape_list.append(
            arcade.shape_list.create_lines_with_colors(
                point_list=points,
                color_list=[DARK_BLUE] * len(points),
                line_width=4,
            ),
        )

    def on_draw(self):  # called every new frame
        self.clear()  # clear previous drawings
        self.create_background()

        self.lines_shape_list.draw()
        self.calamar.draw()

        self.icons.update()
        self.icons.sprite_list.draw()
        self.calamar.check_icon_collisions(self.icons)

        score_manager.draw()
        if not score_manager.time_left:
            high_scores_manager.add_score(score_manager.score)
            self.window.show_view(HighScoresView())

        self.window.ctx.enable_only(self.window.ctx.BLEND)
        self.calamar.draw_fireworks()

    def on_key_press(self, key, modifiers):
        self.calamar.on_key_press(key, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        self.calamar.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        self.calamar.on_mouse_press(x, y, button, modifiers)


class MainWindow(arcade.Window):
    def __init__(self):
        super().__init__(
            width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title="Calamars et Pythons"
        )

        icon_path = files(calp.assets.images) / "icon.png"
        icon_image = pyglet.image.load(icon_path)
        self.set_icon(icon_image)

        background_music = arcade.load_sound(
            files(calp.assets.sounds) / "background_music.mp3"
        )
        arcade.play_sound(background_music, volume=0.4, loop=True)

        arcade.load_font(Path(str(files(calp.assets) / "FiraCode-Regular.ttf")))

        self.show_view(GameView())
