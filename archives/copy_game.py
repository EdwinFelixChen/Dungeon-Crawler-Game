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
from world.dungeongen import DungeonGenerator
from world.room import Room
from world.coin import Coin
from UI.inventory_ui import InventoryUI

class Game:
    def __init__(self):

        pygame.init()

        #load images

        #screen = world - camera
        self.screen_x = 1280
        self.screen_y = 720

        self.screen = pygame.display.set_mode((self.screen_x, self.screen_y))

        #camera
        self.camera = Camera()

        #game state
        self.game_state = "adventure"
        self.possible_game_states = ["adventure", "boss fight", "victory", "defeat", "pre-spawn delay"]
        self.countdown = None

        #rendering and UIs
        self.renderer = Renderer(self.screen)
        self.inventoryUI = InventoryUI()

        #fps
        self.clock = pygame.time.Clock()
        self.clock.tick(60)

        #enemy spawning
        self.spawner = EnemySpawner()
        self.boss = None

        #room spawning and rooms list
        self.dungeongenerator = DungeonGenerator(10)
        self.dungeongenerator.generate()
        self.rooms: list[Room] = self.dungeongenerator.convert(400)
        self.dungeongenerator.add_doors(self.rooms)

        #inventory
        self.inventory = Inventory()
        
        #starting room
        start_room = self.rooms[0]

        #game objects
        self.player = Player(start_room.left + start_room.width / 2, start_room.top + start_room.height / 2, 35, 1, 20)
        self.enemies: list[GroundEnemy] = []
        self.projectiles: list[Projectile] = []
        self.treasures: list[Coin] = []

        #getting input
        self.keys = pygame.key.get_pressed()

        #room hitboxes
        for room in self.rooms:
            for key, value in room.doors.items():
                if value and key in room.door_owners:
                    room.replace_with_door_hitbox(key)

                elif value and key not in room.door_owners:
                    room.remove_wall_hitbox(key)
#UPDATE HELPERS

    #camera offset update
    def update_camera(self):
        #updating camera
        self.camera.update(self.player, self.screen_x, self.screen_y)

    #update game state
    def update_game_state(self):
        uncleared_rooms = [room for room in self.rooms if not room.cleared]

        if len(uncleared_rooms) == 1:
            if uncleared_rooms[0].room_field.contains(self.player.hitbox):
                self.game_state = "pre-spawn delay"
                self.boss_room = uncleared_rooms[0]

        elif len([room for room in self.rooms if not room.cleared]) == 0:
            self.game_state = "victory"

        else:
            self.game_state = "adventure"

    #spawn and de-spawn
    def update_spawn_enemies(self):
        #Enemy spawn
        if self.game_state == "adventure":
            for room in self.rooms:
                if room.room_field.contains(self.player.hitbox):

                    if room.spawned_enemies == False:

                        for _ in range(random.randint(1, 3)):

                            enemy_type, enemy_stats = self.spawner.random_enemy_type()

                            x, y = self.spawner.get_spawn_position(self.player.x, self.player.y, enemy_stats["size"], room)

                            new_enemy = self.spawner.spawn(enemy_type, x, y, room, GroundEnemy)

                            self.enemies.append(new_enemy)

                            room.enemies.append(new_enemy)

                        room.spawned_enemies = True

    def handle_treasures(self):
        for treasure in self.treasures[:]:
            if self.player.hitbox.colliderect(treasure.hitbox):
                self.inventory.add_to_inventory(treasure.name, treasure.quantity)
                self.treasures.remove(treasure)

    def handle_deaths(self):
        #enemy deaths
        for enemy in self.enemies[:]:
            if not enemy.alive:
                self.enemies.remove(enemy)
                self.treasures.append(enemy.death_treasure())

        if self.boss:
            if not self.boss.alive:
                self.boss = None

    def check_room_cleared(self):
        #clear rooms
        for room in self.rooms:
            if room.spawned_enemies and not any(enemy.alive for enemy in room.enemies):
                room.cleared = True

    #PRE-BOSS SPAWN STATE
    def start_timer(self):
        self.countdown = 300

    def update_timer(self):
        self.countdown -= 1

    #leaving the state
    def switch_state(self):
        self.boss = self.spawner.boss_spawn("boss", self.boss_room.center_x, self.boss_room.center_y, self.boss_room, Boss)
        self.game_state = "boss fight"

    def manage_boss_room_collisions(self):
        if not self.boss_room.room_field.contains(self.player.hitbox):
            self.player.move_back_after_hit_wall()
            self.player.update_hitbox()

    #BOSS FIGHT STATE
        #nothing yet!

    #movement
    def update_entities(self):
        #player
        self.player.old_x = self.player.x
        self.player.old_y = self.player.y

        self.player.move(self.keys)

        if self.player.kb_time > 0:
            self.player.update_knockback(self.player.vx, self.player.vy)

        self.player.update_hitbox()

        #enemy
        for enemy in self.enemies:
            if enemy.start_room.room_field.contains(self.player.hitbox):
                enemy.move(self.player.x, self.player.y)

                if enemy.kb_time > 0:
                    enemy.update_knockback(enemy.vx, enemy.vy)
            else:
                enemy.return_to_start()

            enemy.update_hitbox()
            enemy.domain_restriction()

        if self.boss:
            self.boss.domain_restriction()

    #checking collisions
    def handle_projectiles(self):
        #projectile collisions
        for projectile in self.projectiles[:]:
            projectile.update_projectile()
            projectile.update_hitbox()

            if projectile.owner == "player":
                for enemy in self.enemies:
                    if projectile.hitbox.colliderect(enemy.hitbox):
                        enemy.take_damage(1)
                        self.projectiles.remove(projectile)
                        continue

                if self.boss and projectile.hitbox.colliderect(self.boss.hitbox):
                    self.boss.take_damage(1)
                    self.projectiles.remove(projectile)
                    continue

            if projectile.owner in ["enemy", "boss"]:
                if projectile.hitbox.colliderect(self.player.hitbox):
                    self.player.take_damage(1)
                    self.projectiles.remove(projectile)
                    continue

            #check wall collisions
            if projectile in self.projectiles:
                for room in self.rooms:
                    for hitbox in room.wall_hitboxes.values():
                        if hitbox:
                            for segment in hitbox:
                                if segment.colliderect(projectile.hitbox):
                                    self.projectiles.remove(projectile)
                                    continue


    def handle_wall_collisions(self):
            
        #player-wall collisions

        for room in self.rooms:

            for hitbox in room.wall_hitboxes.values():

                if hitbox:

                    for segment in hitbox:

                        if self.player.hitbox.colliderect(segment):

                            self.player.move_back_after_hit_wall()

                            self.player.update_hitbox()

                            return

    def player_enemy_collisions(self):
        for enemy in self.enemies:
            if enemy.kb_time:
                continue
            
            if enemy.hitbox.colliderect(self.player.hitbox):
                self.player.take_damage(2)
                player_dx, player_dy, enemy_dx, enemy_dy = (-d for d in get_direction(self.player, enemy))

                self.player.start_knockback(player_dx, player_dy, 2)
                enemy.start_knockback(enemy_dx, enemy_dy, 2)               

#DRAW HELPERS

    def draw_inventory(self):
        self.inventoryUI.draw_button(self.renderer)

        if self.inventoryUI.inventory_is_open:
            self.inventoryUI.draw_inventory(self.renderer)

    def draw_rooms(self):
        for room in self.rooms:
            for key, value in room.doors.items():
                if not value:
                    room.draw_wall(self.screen, key, self.camera)

                elif key in room.door_owners:
                    room.draw_door_wall(self.screen, key, self.camera)

    def draw_objects(self):
        self.player.draw(self.screen, [0,0,255], self.camera)
        self.player.draw_HP_bar(self.screen, self.camera)

        #drawing enemies
        for enemy in self.enemies:
            enemy.draw_HP_bar(self.screen, self.camera)
            enemy.draw(self.screen, [255,0,0], self.camera)

        #drawing projectiles
        for projectile in self.projectiles:
            if projectile.owner == "player":
                projectile.draw(self.screen, [0,0,255], self.camera)
            else:
                projectile.draw(self.screen, [255,0,0], self.camera)

        #drawing treasures
        for treasure in self.treasures:
            treasure.draw_treasure(self.screen, self.camera)

        if self.game_state == "boss fight":
            self.draw_boss_room()

    #PRE-BOSS SPAWN STATE
    def draw_boss_room(self):
        self.boss_room.draw_full_room(self.screen, self.camera)

    #BOSS FIGHT STATE
    def draw_boss(self):
        self.boss.draw(self.screen, [255,0,0], self.camera)
        self.boss.draw_HP_bar(self.screen, self.camera)

#main game componentsss
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

                if self.player.can_fire():

                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    world_mouse_x, world_mouse_y = self.camera.screen_to_world(mouse_x, mouse_y)

                    projectile = Projectile(self.player.x, self.player.y, world_mouse_x, world_mouse_y, 4, 3, "player")

                    self.projectiles.append(projectile)

                    self.player.last_shot_time = self.player.current_time

    def update_adventure(self):

        self.update_camera()

        self.update_spawn_enemies()

        self.update_entities()

        self.handle_projectiles()

        self.player_enemy_collisions()

        self.handle_treasures()

        self.handle_wall_collisions()

        self.handle_deaths()

        self.check_room_cleared()

        self.update_game_state()

    def draw_adventure(self):
        self.draw_inventory()

        self.draw_rooms()

        self.draw_objects()    

    def update_pre_boss_fight(self):
        if self.countdown == None:
            self.start_timer()

        self.update_timer()

        self.update_camera()

        self.update_entities()

        self.player_enemy_collisions()

        self.manage_boss_room_collisions()

        if self.countdown <= 0:
            self.switch_state()
    def draw_pre_boss_fight(self):
        self.draw_inventory()

        self.draw_boss_room()

        self.draw_objects()
 
    def update_boss_fight(self):
        if self.boss.state_duration <= 0:
            self.boss.change_state()

        self.boss.update_timer()

        self.update_camera()

        self.update_entities()

        if self.boss.state == "walking":
            self.boss.move(self.player.x, self.player.y)

        elif self.boss.state == "aiming":
            if not self.boss.aimed:
                self.boss.aim_at_player(get_direction, self.player)
                self.boss.aimed = True

        elif self.boss.state == "firing":
            if not self.boss.fired:
                self.projectiles.append(self.boss.fire_projectile(Projectile, self.player))
                self.boss.fired = True

        elif self.boss.state == "charging":
            self.boss.update_charge()

        elif self.boss.state == "idling":
            pass

        self.boss.update_hitbox()

        self.handle_projectiles()
        self.handle_wall_collisions()

        self.handle_treasures()
        self.handle_deaths()

        if self.boss == None:
            self.game_state = "adventure"
            self.countdown = None
    def draw_boss_fight(self):
        self.draw_inventory()

        self.draw_boss_room()

        self.draw_objects()

        if self.boss:
            self.draw_boss()

    def run(self):
        self.running = True

        while self.running:
            self.screen.fill((0,0,0))
            
            self.handle_events()

            if self.game_state == "adventure":
                self.update_adventure()

                self.draw_adventure()

            elif self.game_state == "pre-spawn delay":
                self.update_pre_boss_fight()

                self.draw_pre_boss_fight()

            elif self.game_state == "boss fight":
                self.update_boss_fight()

                self.draw_boss_fight()

            pygame.display.update()

