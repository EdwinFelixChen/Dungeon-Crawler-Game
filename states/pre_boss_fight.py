from __future__ import annotations
from states.base_state import BaseState
from typing import TYPE_CHECKING

class PreBossFight(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.duration = None

    def update(self):
        super().update()
        
        if self.duration == None:
            self.start_timer()

        self.update_timer()

        self.game.movement.update_entities()

        self.manage_boss_room_collisions()

        self.change_state()

    def draw(self):
        self.game.renderer.draw_inventory()

        self.draw_boss_room()

        self.game.renderer.draw_entities()

        self.game.renderer.draw_treasures(self.game.boss_room)

    def change_state(self):
        if self.duration <= 0:
            self.duration = None
            self.game.state_manager.change_state(self.game.boss_fight_state)

    def manage_boss_room_collisions(self):
        if not self.game.boss_room.room_field.contains(self.game.player.hitbox):
            self.game.movement.push_into_rect(self.game.player, self.game.boss_room.room_field)
            self.game.player.update_hitbox()

    def draw_boss_room(self):
        for key in self.game.boss_room.wall_hitboxes.keys():
            self.game.boss_room.draw_wall(self.game.screen, key, self.game.camera)

    def start_timer(self):
        self.duration = 300

    def update_timer(self):
        self.duration -= 1

