import math
import random
from importlib.resources import files
from time import perf_counter

import arcade

import calp.assets.images
import calp.calamar
from calp.calamar import Arm, Calamar
from calp.constants import MAX_ALIVE_ICONS, SCREEN_WIDTH


class Icon:
    def __init__(self, is_enemy, angle):
        self.is_enemy = is_enemy
        self.angle = angle
        if self.is_enemy:
            icon = random.choice((
                "c-sharp.png",
                "cpp.png",
                "html-5.png",
                "java.png",
                "js.png",
                "rust.png",
            ))
        else:
            icon = "python.png"
        self.sprite = arcade.Sprite(files(calp.assets.images) / icon, scale=0.1)
        self.sprite.center_x = Arm.CENTER_X + 1000 * math.cos(self.angle)
        self.sprite.center_y = Arm.CENTER_Y + 1000 * math.sin(self.angle)
        self.speed = random.randint(150, 300)  # pixels per second
        self.last_update_date = perf_counter()
        self.to_be_removed = False

    def update(self):
        if self.to_be_removed:
            return
        new_date = perf_counter()
        delta_time = new_date - self.last_update_date
        distance = self.speed * delta_time
        self.sprite.center_x -= distance * math.cos(self.angle)
        self.sprite.center_y -= distance * math.sin(self.angle)
        distance_to_center = math.hypot(
            self.sprite.center_x - Arm.CENTER_X,
            self.sprite.center_y - Arm.CENTER_Y,
        )
        if (
            distance_to_center < calp.calamar.BODY_WIDTH / 2
            or distance_to_center > 1.5 * SCREEN_WIDTH
        ):
            self.to_be_removed = True
        self.last_update_date = new_date


class IconList:
    def __init__(self):
        self.icons = []
        self.sprite_list = arcade.SpriteList()

    def clear(self):
        self.icons.clear()
        self.sprite_list.clear()

    def update(self):
        for icon in self.icons:
            icon.update()

        for icon in list(self.icons):
            if icon.to_be_removed:
                self.icons.remove(icon)
                self.sprite_list.remove(icon.sprite)

        if len(self.icons) < MAX_ALIVE_ICONS:
            icon = Icon(
                random.choice((True, False)),
                math.radians(random.choice(Calamar.ARM_ANGLES)),
            )
            self.icons.append(icon)
            self.sprite_list.append(icon.sprite)

    def __getitem__(self, searched_icon_sprite):
        if isinstance(searched_icon_sprite, arcade.Sprite):
            for icon, sprite in zip(self.icons, self.sprite_list, strict=True):
                if sprite == searched_icon_sprite:
                    return icon
        raise KeyError
