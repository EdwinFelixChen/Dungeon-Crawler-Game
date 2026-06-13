from __future__ import annotations
import pygame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.game import Game
    from core.camera import Camera


class Portal:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen, color_tuple, camera: Camera):
        x, y = camera.world_to_screen(self.x, self.y)

        pygame.draw.rect(screen, color_tuple, (x, y, self.width, self.height))

    