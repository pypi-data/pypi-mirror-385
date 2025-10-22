import math
from importlib.resources import files
from itertools import pairwise
from time import perf_counter

import arcade

import calp.assets.images
import calp.assets.sounds
from calp.constants import BLACK, ORANGE, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
from calp.fireworks import Firework
from calp.score import score_manager

BODY_X = SCREEN_WIDTH / 2
BODY_Y = SCREEN_HEIGHT / 2
BODY_HEIGHT = SCREEN_WIDTH / 6
BODY_WIDTH = SCREEN_WIDTH / 12
BODY_TRIANGLE_WIDTH = SCREEN_WIDTH / 16
EYE_OFFSET_X = BODY_WIDTH / 4
EYE_OFFSET_Y = -BODY_HEIGHT / 2
EYE_RADIUS = BODY_WIDTH / 3
IDLE_ARM_LENGTH = 80

punch = arcade.load_sound(str(files(calp.assets.sounds) / "punch.wav"))
catch = arcade.load_sound(str(files(calp.assets.sounds) / "catch.wav"))
bad_catch = arcade.load_sound(str(files(calp.assets.sounds) / "bad_catch.wav"))


class Arm:
    CENTER_X = SCREEN_WIDTH / 2
    CENTER_Y = BODY_Y + EYE_OFFSET_Y - 10
    SPEED = 1000  # px per seconds

    def __init__(self, angle):
        self.angle = angle
        self.length = IDLE_ARM_LENGTH
        self.length_modification_date = perf_counter()
        self.target_length = IDLE_ARM_LENGTH
        image_path = files(calp.assets.images) / "sucker.png"
        self.sprite = arcade.Sprite(image_path, scale=0.12)
        self.sprite.radians = math.pi - self.angle
        self.non_focused_sprite_width = self.sprite.width
        self.non_focused_sprite_height = self.sprite.height
        self.focused = False
        self.punching = False

    def catch(self):
        self.target_length = 500
        self.punching = False

    def punch(self):
        self.target_length = 500
        self.punching = True

    def end_point(self):
        return (
            self.CENTER_X + self.length * math.cos(self.angle),
            self.CENTER_Y + self.length * math.sin(self.angle),
        )

    def points(self):
        return [
            (self.CENTER_X, self.CENTER_Y - 10),
            (self.CENTER_X, self.CENTER_Y + 10),
            self.end_point(),
        ]

    def update(self):
        new_date = perf_counter()
        delta_time = new_date - self.length_modification_date
        if self.length < self.target_length:
            self.length += delta_time * self.SPEED
            if self.length >= self.target_length:
                self.length = self.target_length
                self.target_length = IDLE_ARM_LENGTH
        elif self.length >= self.target_length:
            self.length -= delta_time * self.SPEED
            self.length = max(self.length, IDLE_ARM_LENGTH)
        self.length_modification_date = new_date
        self.sprite.center_x, self.sprite.center_y = self.end_point()
        if self.focused:
            self.sprite.width = 1.5 * self.non_focused_sprite_width
            self.sprite.height = 1.5 * self.non_focused_sprite_height
        else:
            self.sprite.width = self.non_focused_sprite_width
            self.sprite.height = self.non_focused_sprite_height


class Calamar:
    ARM_ANGLES = (
        -(180 - 10),
        -(180 - 30),
        -30,
        -10,
        10,
        30,
        180 - 30,
        180 - 10,
    )

    def setup(self):
        self.arms = [Arm(angle=math.radians(angle)) for angle in self.ARM_ANGLES]
        self.focus_index = 0
        self.arms[self.focus_index].focused = True

        self.shape_list = arcade.shape_list.ShapeElementList()
        self.setup_body()
        self.setup_face()
        self.setup_arms()

        self.fireworks = []

    def setup_body(self):
        self.shape_list.append(
            arcade.shape_list.create_ellipse_filled(
                center_x=BODY_X,
                center_y=BODY_Y,
                width=BODY_WIDTH,
                height=BODY_HEIGHT,
                color=ORANGE,
            ),
        )
        self.shape_list.append(
            arcade.shape_list.create_ellipse_filled(
                center_x=BODY_X,
                center_y=BODY_Y - BODY_HEIGHT / 2,
                width=BODY_WIDTH,
                height=BODY_WIDTH,
                color=ORANGE,
            ),
        )

        top = (BODY_X, BODY_Y + 3 * BODY_HEIGHT / 4)
        bottom = (BODY_X, BODY_Y + BODY_HEIGHT / 12)
        points = [
            top,
            bottom,
            (BODY_X - BODY_TRIANGLE_WIDTH, BODY_Y + BODY_HEIGHT / 4),
            top,
            bottom,
            (BODY_X + BODY_TRIANGLE_WIDTH, BODY_Y + BODY_HEIGHT / 4),
        ]
        self.shape_list.append(
            arcade.shape_list.create_triangles_filled_with_colors(
                points,
                [ORANGE] * len(points),
            ),
        )

    def setup_face(self):
        self.shape_list.append(
            arcade.shape_list.create_ellipse_filled(
                center_x=BODY_X - EYE_OFFSET_X,
                center_y=BODY_Y + EYE_OFFSET_Y,
                width=EYE_RADIUS,
                height=EYE_RADIUS,
                color=WHITE,
            ),
        )
        self.shape_list.append(
            arcade.shape_list.create_ellipse_filled(
                center_x=BODY_X - EYE_OFFSET_X,
                center_y=BODY_Y + EYE_OFFSET_Y,
                width=EYE_RADIUS / 2,
                height=EYE_RADIUS / 2,
                color=BLACK,
            ),
        )
        self.shape_list.append(
            arcade.shape_list.create_ellipse_filled(
                center_x=BODY_X + EYE_OFFSET_X,
                center_y=BODY_Y + EYE_OFFSET_Y,
                width=EYE_RADIUS,
                height=EYE_RADIUS,
                color=WHITE,
            ),
        )
        self.shape_list.append(
            arcade.shape_list.create_ellipse_filled(
                center_x=BODY_X + EYE_OFFSET_X,
                center_y=BODY_Y + EYE_OFFSET_Y,
                width=EYE_RADIUS / 2,
                height=EYE_RADIUS / 2,
                color=BLACK,
            ),
        )
        points = [
            (BODY_X + EYE_OFFSET_X, BODY_Y + EYE_OFFSET_Y - 20),
            (BODY_X + EYE_OFFSET_X - 10, BODY_Y + EYE_OFFSET_Y - 30),
            (BODY_X - EYE_OFFSET_X + 10, BODY_Y + EYE_OFFSET_Y - 30),
            (BODY_X - EYE_OFFSET_X, BODY_Y + EYE_OFFSET_Y - 20),
        ]
        self.shape_list.append(
            arcade.shape_list.create_line_strip(
                points,
                WHITE,
                line_width=EYE_RADIUS / 4,
            ),
        )

    def setup_arms(self):
        self.arms_shape_list = arcade.shape_list.ShapeElementList()
        self.arms_sprite_list = arcade.SpriteList()
        for arm in self.arms:
            self.arms_sprite_list.append(arm.sprite)

    def update_arms(self):
        self.arms_shape_list.clear()

        points = []
        for arm in self.arms:
            arm.update()
            points.extend(arm.points())

        self.arms_shape_list.append(
            arcade.shape_list.create_triangles_filled_with_colors(
                points,
                [ORANGE] * len(points),
            ),
        )

    def update_fireworks(self):
        # Remove old fireworks
        self.fireworks = [
            firework for firework in self.fireworks if not firework.finished()
        ]

    def draw(self):
        self.update_arms()
        self.update_fireworks()
        self.arms_shape_list.draw()
        self.arms_sprite_list.draw()
        self.shape_list.draw()

    def draw_fireworks(self):
        for firework in self.fireworks:
            firework.render()

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.DOWN:
            self.arms[self.focus_index].catch()
        elif key == arcade.key.UP:
            self.arms[self.focus_index].punch()
        elif key in {arcade.key.LEFT, arcade.key.RIGHT}:
            if key == arcade.key.RIGHT:
                self.focus_arm_by_index((self.focus_index + 1) % 8)
            else:
                self.focus_arm_by_index((self.focus_index - 1) % 8)

    def on_mouse_motion(self, x, y, _dx, _dy):
        self.focus_arm(x, y)

    def on_mouse_press(self, x, y, button, _modifiers):
        self.focus_arm(x, y)
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.arms[self.focus_index].catch()
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.arms[self.focus_index].punch()

    def focus_arm_by_index(self, new_focus_index):
        self.arms[self.focus_index].focused = False
        self.focus_index = new_focus_index
        self.arms[self.focus_index].focused = True

    def focus_arm(self, x, y):
        angle = math.degrees(math.atan2(y - Arm.CENTER_Y, x - Arm.CENTER_X))

        if angle < self.ARM_ANGLES[0]:
            self.focus_arm_by_index(0)
            return

        for previous_arm_index, (previous_arm_angle, next_arm_angle) in enumerate(
            pairwise(self.ARM_ANGLES),
        ):
            if angle < (previous_arm_angle + next_arm_angle) / 2:
                self.focus_arm_by_index(previous_arm_index)
                return

        self.focus_arm_by_index(7)

    def check_icon_collisions(self, icons):
        for arm in self.arms:
            collided_icons_sprites = arcade.check_for_collision_with_list(
                arm.sprite,
                icons.sprite_list,
            )
            if collided_icons_sprites:
                arm.target_length = IDLE_ARM_LENGTH
            for icon_sprite in collided_icons_sprites:
                icon = icons[icon_sprite]
                if arm.punching:
                    arcade.play_sound(punch)
                    self.fireworks.append(Firework(position=arm.end_point()))
                    icon.speed *= -1
                else:
                    if icon.is_enemy:
                        arcade.play_sound(bad_catch)
                        score_manager.enemy_icon_caught()
                    else:
                        arcade.play_sound(catch)
                        score_manager.good_icon_caught()
                    icon.to_be_removed = True
