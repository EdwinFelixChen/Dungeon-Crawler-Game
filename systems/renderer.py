from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.game import Game

class Renderer:
    def __init__(self, game: Game):
        self.game = game

    def draw_sprite(self, image, position):
        self.game.screen.blit(image, position)

    def draw_lobby(self):
        pass

    def draw_inventory(self):
        self.game.inventoryUI.draw_button(self.game.renderer)

        if self.game.inventoryUI.inventory_is_open:
            self.game.inventoryUI.draw_inventory(self.game.renderer)

    def draw_rooms(self):
        for room in self.game.rooms:
            for key, value in room.doors.items():
                if not value:
                    room.draw_wall(self.game.screen, key, self.game.camera)

                elif key in room.door_owners:
                    room.draw_door_wall(self.game.screen, key, self.game.camera)

    def draw_entities(self):
        self.game.player.draw(self.game.screen, [0,0,255], self.game.camera)
        self.game.player.draw_HP_bar(self.game.screen, self.game.camera)

        #drawing enemies
        for enemy in self.game.enemies:
            enemy.draw_HP_bar(self.game.screen, self.game.camera)
            enemy.draw(self.game.screen, [255,0,0], self.game.camera)

        #drawing projectiles
        for projectile in self.game.projectiles:
            if projectile.owner == "player":
                projectile.draw(self.game.screen, [0,0,255], self.game.camera)
            else:
                projectile.draw(self.game.screen, [255,0,0], self.game.camera)

    def draw_treasures(self, room=None):
        self.room = room

        for treasure in self.game.treasures:
            if not room:
                treasure.draw_treasure(self.game.screen, self.game.camera)

            elif treasure.room == room:
                treasure.draw_treasure(self.game.screen, self.game.camera)
            

#main game componentsss