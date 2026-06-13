from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from entities.player import Player

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.camera_x = 0
        self.camera_y = 0

    def update(self, target: Player, screen_x, screen_y):
        self.camera_x = target.x - screen_x / 2
        self.camera_y = target.y - screen_y / 2

    def world_to_screen(self, px, py):
        return px - self.camera_x, py - self.camera_y
    
    def screen_to_world(self, px, py):
        return px + self.camera_x, py + self.camera_y