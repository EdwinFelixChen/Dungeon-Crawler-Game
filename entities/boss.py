from __future__ import annotations
import pygame
from typing import TYPE_CHECKING
from entities.player import Player
from entities.projectile import Projectile
from entities.entity import Entity
from world.coin import Coin
if TYPE_CHECKING:
    from world.room import Room


class Boss(Entity):
    def __init__(self, x, y, size, hp, collide_damage, speed, kb_speed, start_room: Room, type, treasure_drop, projectile_radius):
        super().__init__(x, y, size, hp, max_hp=hp)

        #TOP-LEVEL INFO

        #states
        self.possible_states = ["walking", "aiming", "charging", "firing", "knocked back"]
        self.state_progression = ["walking", "aiming", "firing", "walking", "aiming", "charging"]
        self.state_index = 0
        self.state = None
        self.state_duration = 200

        self.type = type
        self.treasure_drop = treasure_drop
        self.start_room = start_room

        self.boss_spawned = False
        self.aimed = False
        self.fired = False
        self.alive = True

        self.start_x = x
        self.start_y = y

        self.projectile_radius = projectile_radius

        self.speed = speed
        self.charge_speed = 7
        self.projectile_speed = 3
        self.kb_speed = kb_speed

        self.collide_damage = collide_damage

    def change_state(self):
        if self.state_index == len(self.state_progression) - 1:
            self.state_index = 0
            self.state = self.state_progression[self.state_index]
            self.fired = False
            self.aimed = False
            
        else:
            self.state_index += 1
            self.state = self.state_progression[self.state_index]

        self.state_duration = 200

    def update_timer(self):
        self.state_duration -= 1

    def move(self, px, py):
        if self.x < px:
            self.x += self.speed
        elif self.x > px:
            self.x -= self.speed
        if self.y < py:
            self.y += self.speed
        elif self.y > py:
            self.y -= self.speed

    def aim_at_player(self, get_direction, player: Player):
        self.dx, self.dy, _, _ = get_direction(self, player)

        self.vx = self.dx * self.charge_speed
        self.vy = self.dy * self.charge_speed

    def update_charge(self):
        self.x += self.vx
        self.y += self.vy

    def fire_projectile(self, projectile: Projectile, player: Player):
        return projectile(self.x, self.y, player.x, player.y, self.projectile_radius, self.projectile_speed, "boss")

    def domain_restriction(self):
        if not self.start_room.room_field.contains(self.hitbox):
            self.x = max(self.start_room.left + self.size / 2, min(self.x, self.start_room.right - self.size / 2))
            self.y = max(self.start_room.top + self.size / 2, min(self.y, self.start_room.bottom - self.size / 2))

    def return_to_start(self):
        self.move(self.start_x, self.start_y)

    def die(self):
        self.alive = False

    def death_treasure(self):
        return Coin(self.x, self.y, 'gold coins', self.treasure_drop)