from __future__ import annotations
import pygame
from core.camera import Camera
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.enemy import GroundEnemy

class Room:
    def __init__(self, x, y, width, height):
        #positions and lengths
        self.left = x
        self.top = y
        self.right = x + width
        self.bottom = y + height
        self.width = width
        self.height = height
        self.center_y = self.top + self.height / 2
        self.center_x = self.left + self.width / 2

        #room info
        self.enemies: list[GroundEnemy] = []
        self.cleared = False

        #ownership
        self.door_owners = ["left", "top"]

        #hitboxes
        self.wall_hitboxes = {
            "left": [pygame.Rect(self.left, self.top, 2, self.height)],
            "right": [pygame.Rect(self.right + 1, self.top, 2, self.height)],
            "top": [pygame.Rect(self.left, self.top, self.width, 2)],
            "bottom": [pygame.Rect(self.left, self.bottom + 1, self.width, 2)]
        }

        #doors
        self.doors = {
            "left": False,
            "right": False, 
            "top": False,
            "bottom": False
        }

        #to check if in room
        self.room_field = pygame.Rect(self.left, self.top, self.width, self.height)

        #check if enemies spawned
        self.spawned_enemies = False

    def replace_with_door_hitbox(self, side):
        door_size = 80

        match side:
            case "left":
                self.wall_hitboxes["left"] = [
                    pygame.Rect(self.left, self.top, 2, self.center_y - door_size / 2 - self.top),
                    pygame.Rect(self.left, self.center_y + door_size / 2, 2, self.center_y - door_size / 2 - self.top)
                ]

            case "right":
                self.wall_hitboxes["right"] = [
                    pygame.Rect(self.right + 1, self.top, 2, self.center_y - door_size / 2 - self.top),
                    pygame.Rect(self.right + 1, self.center_y + door_size / 2, 2, self.center_y - door_size / 2 - self.top)
                ]

            case "top":
                self.wall_hitboxes["top"] = [
                    pygame.Rect(self.left, self.top, self.center_x - door_size / 2 - self.left, 2),
                    pygame.Rect(self.center_x + door_size / 2, self.top, self.center_x - door_size / 2 - self.left, 2)
                ]

            case "bottom":
                self.wall_hitboxes["bottom"] = [
                    pygame.Rect(self.left, self.bottom + 1, self.center_x - door_size / 2 - self.left, 2),
                    pygame.Rect(self.center_x + door_size / 2, self.bottom + 1, self.center_x - door_size / 2 - self.left, 2)
                ]

    def remove_wall_hitbox(self, side):
        self.wall_hitboxes[side] = []

    def draw_wall(self, screen, side, camera: Camera):

        left, top = camera.world_to_screen(self.left, self.top)
        right, bottom = camera.world_to_screen(self.right, self.bottom)

        match side:
            case "left":
                pygame.draw.line(screen, [255,255,255], (left, top), (left, bottom), 2)

            case "right":
                pygame.draw.line(screen, [255,255,255], (right, top), (right, bottom), 2)

            case "top":
                pygame.draw.line(screen, [255,255,255], (left, top), (right, top), 2)

            case "bottom":
                pygame.draw.line(screen, [255,255,255], (left, bottom), (right, bottom), 2)

    def draw_door_wall(self, screen, side, camera: Camera):

        center_x, center_y = camera.world_to_screen(self.center_x, self.center_y)

        left, top = camera.world_to_screen(self.left, self.top)
        right, bottom = camera.world_to_screen(self.right, self.bottom)

        door_size = 80

        match side:
            case "left":
                pygame.draw.line(screen, [255,255,255], (left, top), (left, center_y - door_size / 2), 2)
                pygame.draw.line(screen, [255,255,255], (left, center_y + door_size / 2), (left, bottom), 2)

            case "right":
                pygame.draw.line(screen, [255,255,255], (right, top), (right, center_y - door_size / 2), 2)
                pygame.draw.line(screen, [255,255,255], (right, center_y + door_size / 2), (right, bottom), 2)

            case "top":
                pygame.draw.line(screen, [255,255,255], (left, top), (center_x - door_size / 2, top), 2)
                pygame.draw.line(screen, [255,255,255], (center_x + door_size / 2, top), (right, top), 2)

            case "bottom":
                pygame.draw.line(screen, [255,255,255], (left, bottom), (center_x - door_size / 2, bottom), 2)
                pygame.draw.line(screen, [255,255,255], (center_x + door_size / 2, bottom), (right, bottom), 2)

    def draw_full_room(self, screen, camera: Camera):
        x, y = camera.world_to_screen(self.left, self.top)
        pygame.draw.rect(screen, [255,255,255], (x, y, self.width, self.height), 2)