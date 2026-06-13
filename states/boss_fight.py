from __future__ import annotations
from typing import TYPE_CHECKING
from entities.projectile import Projectile
from entities.boss import Boss
from core.utility import get_direction
from states.base_state import BaseState


class BossFight(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.duration = None
        self.spawned = False

    def update(self):
        super().update()

        if not self.spawned:
            self.spawn_boss()
            self.game.boss.state = self.game.boss.state_progression[self.game.boss.state_index]
            self.spawned = True

        self.game.boss.update_timer()

        self.game.movement.update_entities()

        if self.game.boss.state == "walking":
            self.game.boss.move(self.game.player.x, self.game.player.y)

        elif self.game.boss.state == "aiming":
            if not self.game.boss.aimed:
                self.game.boss.aim_at_player(get_direction, self.game.player)
                self.game.boss.aimed = True

        elif self.game.boss.state == "firing":
            if not self.game.boss.fired:
                self.game.projectiles.append(self.game.boss.fire_projectile(Projectile, self.game.player))
                self.game.boss.fired = True

        elif self.game.boss.state == "charging":
            self.game.boss.update_charge()
            if self.game.boss.hitbox.colliderect(self.game.player.hitbox):
                self.game.boss.change_state()

            if not self.game.boss_room.room_field.contains(self.game.boss.hitbox):
                self.game.boss.change_state()

        elif self.game.boss.state == "idling":
            pass

        self.game.boss.update_hitbox()

        self.game.combat.handle_projectiles()

        self.game.combat.start_knockback()

        self.game.combat.update_knockback()

        self.game.boss.domain_restriction()
        
        self.game.movement.handle_wall_collisions()

        # safety net: stop player from leaving through door gaps
        if not self.game.boss_room.room_field.contains(self.game.player.hitbox):
            self.game.movement.push_into_rect(self.game.player, self.game.boss_room.room_field)
            self.game.player.update_hitbox()

        if self.game.boss.state_duration <= 0:
            self.game.boss.change_state()

        self.game.combat.handle_deaths()

        self.handle_treasures()

        self.change_state()

    def draw(self):
        self.game.renderer.draw_inventory()

        self.draw_boss_room()

        self.game.renderer.draw_entities()

        self.game.renderer.draw_treasures(self.game.boss_room)

        if self.game.boss:
            self.draw_boss()

    def change_state(self):
        if self.game.boss == None:
            self.duration = None
            self.spawned = False
            self.game.state_manager.change_state(self.game.post_boss_fight_state)

    def spawn_boss(self):
        self.game.boss = self.game.spawner.boss_spawn("boss", self.game.boss_room.center_x, self.game.boss_room.center_y, self.game.boss_room, Boss)

    def manage_boss_room_collisions(self):
        if not self.game.boss_room.room_field.contains(self.game.player.hitbox):
            self.game.movement.push_into_rect(self.game.player, self.game.boss_room.room_field)
            self.game.player.update_hitbox()

    def draw_boss_room(self):
        for key in self.game.boss_room.wall_hitboxes.keys():
            self.game.boss_room.draw_wall(self.game.screen, key, self.game.camera)

    def draw_boss(self):
        self.game.boss.draw(self.game.screen, [255,0,0], self.game.camera)
        self.game.boss.draw_HP_bar(self.game.screen, self.game.camera)

    def start_timer(self):
        self.duration = 200

    def update_timer(self):
        self.duration -= 1

    def handle_treasures(self):
        for treasure in self.game.treasures[:]:
            if self.game.player.hitbox.colliderect(treasure.hitbox):
                self.game.inventory.add_to_inventory(treasure.name, treasure.quantity)
                self.game.treasures.remove(treasure)