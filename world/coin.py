from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.camera import Camera

class Coin:
    def __init__(self, x, y, name, quantity, room):
        self.radius = 4
        self.name = name
        self.quantity = quantity
        self.x = x
        self.y = y
        self.room = room
        self.hitbox = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw_treasure(self, screen, camera: Camera):
        x, y = camera.world_to_screen(self.x, self.y)
        pygame.draw.circle(screen, [255, 215, 0], (x, y), self.radius)