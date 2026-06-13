from __future__ import annotations
import random
from entities.enemy import GroundEnemy
from states.base_state import BaseState
from typing import TYPE_CHECKING


class Adventure(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.spawned_rooms = False
        self.final_room = None

    def update(self):
        if not self.spawned_rooms:
            self.generate_rooms()
            self.game.player.x = self.game.start_room.center_x
            self.game.player.y = self.game.start_room.center_y
            self.spawned_rooms = True

        super().update()

        self.spawn_enemies()

        self.game.movement.update_entities()

        self.game.combat.handle_projectiles()

        self.game.combat.start_knockback()

        self.game.combat.update_knockback()

        self.game.movement.handle_wall_collisions()

        self.game.combat.handle_deaths()

        self.handle_treasures()

        self.check_room_cleared()

        self.change_state()

    def draw(self):
        self.game.renderer.draw_inventory()

        self.game.renderer.draw_rooms()

        self.game.renderer.draw_entities()

        self.game.renderer.draw_treasures()

    def change_state(self):
        uncleared_rooms = [room for room in self.game.rooms if not room.cleared]

        if len(uncleared_rooms) == 1:
            self.final_room = uncleared_rooms[0]

        if not uncleared_rooms:
            if self.final_room.room_field.contains(self.game.player.hitbox):
                self.spawned_rooms = False
                self.game.boss_room = self.final_room
                self.game.state_manager.change_state(self.game.pre_boss_fight_state)

    def generate_rooms(self):
        self.game.dungeongenerator.generate(2)
        self.game.rooms = self.game.dungeongenerator.convert(400)
        self.game.dungeongenerator.add_doors(self.game.rooms)
        self.game.start_room = self.game.rooms[0]

        for room in self.game.rooms:
            for key, value in room.doors.items():
                if value and key in room.door_owners:
                    room.replace_with_door_hitbox(key)

                elif value and key not in room.door_owners:
                    room.remove_wall_hitbox(key)

    def spawn_enemies(self):
        #Enemy spawn
        for room in self.game.rooms:
            if room.room_field.contains(self.game.player.hitbox) and not room.spawned_enemies:

                    for _ in range(random.randint(1, 3)):

                        enemy_type, enemy_stats = self.game.spawner.random_enemy_type()

                        x, y = self.game.spawner.get_spawn_position(self.game.player.x, self.game.player.y, enemy_stats["size"], room)

                        new_enemy = self.game.spawner.spawn(enemy_type, x, y, room, GroundEnemy)

                        self.game.enemies.append(new_enemy)

                        room.enemies.append(new_enemy)

                    room.spawned_enemies = True

    def handle_treasures(self):
        for treasure in self.game.treasures[:]:
            if self.game.player.hitbox.colliderect(treasure.hitbox):
                self.game.inventory.add_to_inventory(treasure.name, treasure.quantity)
                self.game.treasures.remove(treasure)

    def check_room_cleared(self):
        #clear rooms
        for room in self.game.rooms:
            if room.spawned_enemies and not any(enemy.alive for enemy in room.enemies):
                room.cleared = True

                


