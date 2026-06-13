from __future__ import annotations

import pygame
from core.camera import Camera
from world.coin import Coin
from entities.entity import Entity

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from world.room import Room

class GroundEnemy(Entity):
    def __init__(self, x, y, size, hp, collide_damage, speed, kb_speed, start_room: Room, type, treasure_drop):
        #uses center coordinates

        super().__init__(x, y, size, hp, max_hp=hp)
        #top-level info
        self.type = type
        self.treasure_drop = treasure_drop
        self.start_room = start_room
        self.start_x = x
        self.start_y = y
        self.speed = speed
        self.collide_damage = collide_damage
        self.kb_speed = kb_speed

    def move(self, px, py):
        if self.x < px:
            self.x += self.speed
        elif self.x > px:
            self.x -= self.speed
        if self.y < py:
            self.y += self.speed
        elif self.y > py:
            self.y -= self.speed

    def domain_restriction(self):
        if not self.start_room.room_field.contains(self.hitbox):
            self.x = max(self.start_room.left + self.size / 2, min(self.x, self.start_room.right - self.size / 2))
            self.y = max(self.start_room.top + self.size / 2, min(self.y, self.start_room.bottom - self.size / 2))

    def return_to_start(self):
        self.move(self.start_x, self.start_y)

    def death_treasure(self):
        
        return Coin(self.x, self.y, 'gold coins', self.treasure_drop, self.start_room)