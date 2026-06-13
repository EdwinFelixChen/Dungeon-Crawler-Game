from states.base_state import BaseState
from world.portal import Portal
from world.room import Room
import pygame

class Lobby(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.player_spawned = False
        #corner coordinates
        self.lobby_x = 0
        self.lobby_y = 0
        self.lobby_width = 1000
        self.lobby_height = 500

        self.portal_width = 20
        self.portal_height = 70

        self.lobby = Room(
            self.lobby_x,
            self.lobby_y,
            self.lobby_width,
            self.lobby_height
        )
        
    def update(self):
        if not self.player_spawned:
            self.game.player.alive = True
            self.game.player.hp = self.game.player.max_hp
            self.game.player.x = self.lobby_x + self.lobby_width / 2
            self.game.player.y = self.lobby_y + self.lobby_height / 2
            self.create_portal()
            self.player_spawned = True

        super().update()
            
        self.game.movement.update_entities()

        self.game.movement.handle_wall_collisions(self.lobby)

        self.change_state()

    def draw(self): #add camera comversions
        self.portal.draw(self.game.screen, [0,0,255], self.game.camera)

        x, y = self.game.camera.world_to_screen(self.lobby_x, self.lobby_y)
        pygame.draw.rect(self.game.screen, [255,255,255], [x, y, self.lobby_width, self.lobby_height], 2)
        
        self.game.renderer.draw_entities()
        self.game.renderer.draw_inventory()

    def change_state(self):
        if self.game.player.hitbox.colliderect(self.portal.hitbox):
            self.player_spawned = False
            self.game.state_manager.change_state(self.game.adventure_state)

    def create_portal(self):
        self.portal = Portal(
            self.lobby_x + self.lobby_width - self.portal_width,
            self.lobby_y + self.lobby_height / 2 - self.portal_height / 2,
            self.portal_width, 
            self.portal_height
        )
            