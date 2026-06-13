from __future__ import annotations
from typing import TYPE_CHECKING
from states.base_state import BaseState
from world.portal import Portal

class PostBossFight(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.portal_width = 20
        self.portal_height = 70
        self.duration = None
        self.portal = None

    def update(self):
        if self.duration == None:
            self.start_timer()

        self.update_timer()

        if not self.portal and self.duration <= 0:
            self.create_portal()

        super().update()

        self.game.movement.update_entities()

        self.game.combat.handle_projectiles()

        self.game.movement.handle_wall_collisions()

        self.handle_treasures()

        if self.portal:
            self.change_state()

    def draw(self):
        if self.portal:
            self.portal.draw(self.game.screen, [0,0,255], self.game.camera)

        self.game.renderer.draw_rooms()

        self.game.renderer.draw_entities()

        self.game.renderer.draw_treasures()

        self.game.renderer.draw_inventory()

    def change_state(self):
        if self.game.player.hitbox.colliderect(self.portal.hitbox):
            self.game.boss_room = None
            self.duration = None
            self.portal = None
            self.game.rooms = []
            self.game.enemies.clear()
            self.game.projectiles.clear()
            self.game.treasures.clear()
            self.game.boss = None

            # reset adventure so it generates fresh rooms next time
            self.game.boss_fight_state.spawned = False
            self.game.pre_boss_fight_state.duration = None
            self.game.adventure_state.spawned_rooms = False
            self.game.adventure_state.final_room = None
            self.game.state_manager.change_state(self.game.lobby_state)

    def create_portal(self):
        self.portal = Portal(
            self.game.boss_room.center_x - self.portal_width / 2, 
            self.game.boss_room.center_y - self.portal_height / 2,
            self.portal_width,
            self.portal_height
        )

    def handle_treasures(self):
        for treasure in self.game.treasures[:]:
            if self.game.player.hitbox.colliderect(treasure.hitbox):
                self.game.inventory.add_to_inventory(treasure.name, treasure.quantity)
                self.game.treasures.remove(treasure)

    def start_timer(self):
        self.duration = 250

    def update_timer(self):
        self.duration -= 1
    