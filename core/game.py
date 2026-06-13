import pygame
import random
from core.camera import Camera
from systems.renderer import Renderer
from core.utility import get_direction
from entities.player import Player
from entities.enemy import GroundEnemy
from entities.boss import Boss
from entities.projectile import Projectile
from systems.spawner import EnemySpawner
from systems.inventory import Inventory
from systems.combat import Combat
from systems.movement import Movement
from world.dungeongen import DungeonGenerator
from world.room import Room
from world.coin import Coin
from states.lobby import Lobby
from states.adventure import Adventure
from states.pre_boss_fight import PreBossFight
from states.boss_fight import BossFight
from states.post_boss_fight import PostBossFight
from states.manager import StateManager
from UI.inventory_ui import InventoryUI

class Game:
    def __init__(self):

        #game info
        pygame.init()
        self.clock = pygame.time.Clock()
        self.clock.tick(60)
        self.screen_x = 1280
        self.screen_y = 720
        self.screen = pygame.display.set_mode((self.screen_x, self.screen_y))

        #core objects
        self.camera: Camera = Camera()
        self.renderer: Renderer = Renderer(self)
        self.inventory: Inventory = Inventory(self)
        self.inventoryUI: InventoryUI = InventoryUI()
        self.spawner: EnemySpawner = EnemySpawner()
        self.movement = Movement(self)
        self.enemies: list[GroundEnemy] = []
        self.projectiles: list[Projectile] = []
        self.treasures: list[Coin] = []
        self.dungeongenerator: DungeonGenerator = DungeonGenerator()
        self.player: Player = Player(0, 0, 35, 1, 1, 20)
        self.rooms: list[Room] = []
        self.start_room: Room | None = None
        self.boss: Boss | None = None
        self.boss_room: Room | None = None

        #combat and states (need player to exist first)
        self.lobby_state: Lobby = Lobby(self)
        self.combat: Combat = Combat(self)
        self.state_manager: StateManager = StateManager()
        self.adventure_state: Adventure = Adventure(self)
        self.pre_boss_fight_state: PreBossFight = PreBossFight(self)
        self.boss_fight_state: BossFight = BossFight(self)
        self.post_boss_fight_state: PostBossFight = PostBossFight(self)
        self.state_manager.current_state = self.lobby_state

        #getting input
        self.keys = pygame.key.get_pressed()

#UPDATE HELPERS

#MAIN COMPONENTS
    def handle_events(self):
        #getting input
        self.keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if self.inventoryUI.button_hitbox.collidepoint(mouse_pos):

                    self.inventoryUI.inventory_is_open = True

                if self.inventoryUI.close_hitbox.collidepoint(mouse_pos):

                    self.inventoryUI.inventory_is_open = False

                if self.player.can_fire() and self.state_manager.current_state not in [self.lobby_state, self.pre_boss_fight_state]:

                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    world_mouse_x, world_mouse_y = self.camera.screen_to_world(mouse_x, mouse_y)

                    projectile = Projectile(self.player.x, self.player.y, world_mouse_x, world_mouse_y, 4, 3, "player")

                    self.projectiles.append(projectile)

                    self.player.last_shot_time = self.player.current_time  

    def run(self):
        self.running = True

        while self.running:
            self.screen.fill((0,0,0))
            
            self.handle_events()

            self.state_manager.update()

            self.state_manager.draw()

            pygame.display.update()

