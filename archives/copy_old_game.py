import pygame
import random

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
        self.dungeongenerator = DungeonGenerator(2)
        self.dungeongenerator.generate()
        self.rooms: list[Room] = self.dungeongenerator.convert(400)
        self.dungeongenerator.add_doors(self.rooms)

        #inventory
        self.inventory = Inventory()
        
        #starting room
        start_room = self.rooms[0]

        #game objects
        self.player = Player(start_room.left + start_room.width / 2, start_room.top + start_room.height / 2, 35, 1, 20)
        self.enemies: list[Enemy] = []
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

    #helper functions
    def get_direction(self, object, target):
        dx = target.x - object.x
        dy = target.y - object.y

        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance == 0:
            return 0, 0, 0, 0

        object_dx = dx / distance 
        object_dy = dy / distance

        target_dx = -dx / distance 
        target_dy = -dy / distance 

        return object_dx, object_dy, target_dx, target_dy

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

                            new_enemy = self.spawner.spawn(enemy_type, x, y, room, Enemy)

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
                player_dx, player_dy, enemy_dx, enemy_dy = (-d for d in self.get_direction(self.player, enemy))

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
            self.boss.state_switch()

        self.boss.state_countdown()

        self.update_camera()

        self.update_entities()

        if self.boss.state == "walking":
            self.boss.walk(self.player.x, self.player.y)

        elif self.boss.state == "aiming":
            if not self.boss.aimed:
                self.boss.aim_at_player(self.get_direction, self.player)
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

#camera system
class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

    def update(self, target, screen_x, screen_y):
        self.camera_x = target.x - screen_x / 2
        self.camera_y = target.y - screen_y / 2

    def world_to_screen(self, px, py):
        return px - self.camera_x, py - self.camera_y
    
    def screen_to_world(self, px, py):
        return px + self.camera_x, py + self.camera_y

#UI system
class Renderer:
    def __init__(self, screen):
        self.screen = screen

    def draw_sprite(self, image, position):
        self.screen.blit(image, position)

class InventoryUI:
    def __init__(self):
        #sprite sheets
        self.button_sheet = pygame.image.load("assets/UI_pack/PNG/Buttons.png")
        self.inventory_sheet = pygame.image.load("assets/UI_pack/PNG/Inventory.png")

        #inventory button
        self.button_rect = pygame.Rect(94, 338, 56, 12)
        self.button_image = self.button_sheet.subsurface(self.button_rect)
        self.button_image = pygame.transform.scale(self.button_image, (112, 24))
        self.button_pos = (1148, 20)
        self.update_button_hitbox()

        #slotted inventory screen
        sf = 4
        self.inventory_rect = pygame.Rect(118, 0, 98, 102)
        self.inventory_image = self.inventory_sheet.subsurface(self.inventory_rect)
        inv_width = 98 * sf
        inv_height = 102 * sf
        self.inventory_image = pygame.transform.scale(self.inventory_image, (inv_width, inv_height))
        self.inventory_is_open = False
        self.inventory_pos = (640 - inv_width / 2, 360 - inv_height / 2)
        self.inv_x, self.inv_y = self.inventory_pos

        self.close_x = 2 * sf
        self.close_y = 2 * sf
        self.close_dim = 10 * sf
        self.close_pos = (self.inv_x + inv_width - self.close_dim - self.close_x, self.inv_y + self.close_y)
        self.update_close_hitbox()


    def update_button_hitbox(self):
        self.button_hitbox = pygame.Rect(
            self.button_pos[0],
            self.button_pos[1],
            self.button_image.get_width(),
            self.button_image.get_height()
        )

    def update_close_hitbox(self):
        self.close_hitbox = pygame.Rect(
            self.close_pos[0],
            self.close_pos[1],
            self.close_dim,
            self.close_dim
        )


    def draw_button(self, renderer):
        renderer.draw_sprite(self.button_image, self.button_pos)

    def draw_inventory(self, renderer):
        renderer.draw_sprite(self.inventory_image, self.inventory_pos)

#Inventory system

class Inventory:
    def __init__(self):
        self.inventory = {}

    def add_to_inventory(self, item, quantity=None, description=None):
        if item not in self.inventory:
            self.inventory[item] = {"quantity": quantity, "description": description}

        else:
            self.inventory[item]['quantity'] += quantity

    def access_inventory(self, draw_sprite):
        draw_sprite()
        
class Coin:
    def __init__(self, x, y, name, quantity):
        self.radius = 4
        self.name = name
        self.quantity = quantity
        self.x = x
        self.y = y
        self.hitbox = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw_treasure(self, screen, camera):
        x, y = camera.world_to_screen(self.x, self.y)
        pygame.draw.circle(screen, [255, 215, 0], (x, y), self.radius)

#rooms system      
class DungeonGenerator:

    def __init__(self, number_of_rooms):
        self.num = number_of_rooms

    def generate(self):
        self.positions = [(0,0)]

        for _ in range(self.num - 1):
            position_index = random.randint(0, len(self.positions) - 1)
            
            base_x, base_y = self.positions[position_index]

            while True:

                axis = random.choice([1, 2])

                x, y = base_x, base_y

                if axis == 1:
                    x += random.choice([1, -1])

                else:
                    y += random.choice([1, -1])

                if (x, y) not in self.positions:
                    self.positions.append((x, y))
                    break

    def convert(self, room_size):
        rooms = []

        screen_width = 1280
        screen_height = 720

        offset_x = screen_width/2 - room_size/2
        offset_y = screen_height/2 - room_size/2

        for x, y in self.positions:
            position_x = x * room_size + offset_x
            position_y = y * room_size + offset_y

            room = Room(position_x, position_y, room_size, room_size)
            
            rooms.append(room)

        return rooms

    def add_doors(self, rooms):
        #positions and doors list must match in order

        room_index = 0

        for x, y in self.positions:

            if (x + 1, y) in self.positions:

                rooms[room_index].doors["right"] = True
            
            if (x - 1, y) in self.positions:

                rooms[room_index].doors["left"] = True

            if (x, y + 1) in self.positions:

                rooms[room_index].doors["bottom"] = True

            if (x, y - 1) in self.positions:

                rooms[room_index].doors["top"] = True

            room_index += 1

class Room:
    def __init__(self, x, y, width, height):
        #positions and lengths
        self.left = x
        self.top = y
        self.right = x + width
        self.bottom = y + height
        self.width = width
        self.height = height
        self.center_y = self.top + self.height / 2
        self.center_x = self.left + self.width / 2

        #room info
        self.enemies: list[Enemy] = []
        self.cleared = False

        #ownership
        self.door_owners = ["left", "top"]

        #hitboxes
        self.wall_hitboxes = {
            "left": [pygame.Rect(self.left, self.top, 2, self.height)],
            "right": [pygame.Rect(self.right + 1, self.top, 2, self.height)],
            "top": [pygame.Rect(self.left, self.top, self.width, 2)],
            "bottom": [pygame.Rect(self.left, self.bottom + 1, self.width, 2)]
        }

        #doors
        self.doors = {
            "left": False,
            "right": False, 
            "top": False,
            "bottom": False
        }

        #to check if in room
        self.room_field = pygame.Rect(self.left, self.top, self.width, self.height)

        #check if enemies spawned
        self.spawned_enemies = False

    def replace_with_door_hitbox(self, side):
        door_size = 80

        match side:
            case "left":
                self.wall_hitboxes["left"] = [
                    pygame.Rect(self.left, self.top, 2, self.center_y - door_size / 2 - self.top),
                    pygame.Rect(self.left, self.center_y + door_size / 2, 2, self.center_y - door_size / 2 - self.top)
                ]

            case "right":
                self.wall_hitboxes["right"] = [
                    pygame.Rect(self.right, self.top, 2, self.center_y - door_size / 2 - self.top),
                    pygame.Rect(self.right, self.center_y + door_size / 2, 2, self.center_y - door_size / 2 - self.top)
                ]

            case "top":
                self.wall_hitboxes["top"] = [
                    pygame.Rect(self.left, self.top, self.center_x - door_size / 2 - self.left, 2),
                    pygame.Rect(self.center_x + door_size / 2, self.top, self.center_x - door_size / 2 - self.left, 2)
                ]

            case "bottom":
                self.wall_hitboxes["bottom"] = [
                    pygame.Rect(self.left, self.bottom, self.center_x - door_size / 2 - self.left, 2),
                    pygame.Rect(self.center_x + door_size / 2, self.bottom, self.center_x - door_size / 2 - self.left, 2)
                ]

    def remove_wall_hitbox(self, side):
        self.wall_hitboxes[side] = []

    def draw_wall(self, screen, side, camera: Camera):

        left, top = camera.world_to_screen(self.left, self.top)
        right, bottom = camera.world_to_screen(self.right, self.bottom)

        match side:
            case "left":
                pygame.draw.line(screen, [255,255,255], (left, top), (left, bottom), 2)

            case "right":
                pygame.draw.line(screen, [255,255,255], (right, top), (right, bottom), 2)

            case "top":
                pygame.draw.line(screen, [255,255,255], (left, top), (right, top), 2)

            case "bottom":
                pygame.draw.line(screen, [255,255,255], (left, bottom), (right, bottom), 2)

    def draw_door_wall(self, screen, side, camera: Camera):

        center_x, center_y = camera.world_to_screen(self.center_x, self.center_y)

        left, top = camera.world_to_screen(self.left, self.top)
        right, bottom = camera.world_to_screen(self.right, self.bottom)

        door_size = 80

        match side:
            case "left":
                pygame.draw.line(screen, [255,255,255], (left, top), (left, center_y - door_size / 2), 2)
                pygame.draw.line(screen, [255,255,255], (left, center_y + door_size / 2), (left, bottom), 2)

            case "right":
                pygame.draw.line(screen, [255,255,255], (right, top), (right, center_y - door_size / 2), 2)
                pygame.draw.line(screen, [255,255,255], (right, center_y + door_size / 2), (right, bottom), 2)

            case "top":
                pygame.draw.line(screen, [255,255,255], (left, top), (center_x - door_size / 2, top), 2)
                pygame.draw.line(screen, [255,255,255], (center_x + door_size / 2, top), (right, top), 2)

            case "bottom":
                pygame.draw.line(screen, [255,255,255], (left, bottom), (center_x - door_size / 2, bottom), 2)
                pygame.draw.line(screen, [255,255,255], (center_x + door_size / 2, bottom), (right, bottom), 2)

    def draw_full_room(self, screen, camera: Camera):
        x, y = camera.world_to_screen(self.left, self.top)
        pygame.draw.rect(screen, [255,255,255], (x, y, self.width, self.height), 2)

#object systems
class Projectile:
    def __init__(self, object_x, object_y, target_x, target_y, radius, speed, owner):

        self.x = object_x
        self.y = object_y

        self.target_x = target_x
        self.target_y = target_y

        self.radius = radius

        self.speed = speed

        self.vel_x = 0
        self.vel_y = 0

        self.owner = owner

        self.get_velocity()

        self.update_hitbox()


    def get_velocity(self):

        dx = self.target_x - self.x
        dy = self.target_y - self.y

        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance == 0:
            return

        self.vel_x = dx / distance * self.speed
        self.vel_y = dy / distance * self.speed

    def update_projectile(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def update_hitbox(self):
        self.hitbox = pygame.Rect(self.x - self.radius/2, self.y - self.radius/2, self.radius * 2, self.radius * 2)

    def draw(self, screen, color_tuple, camera: Camera):
        x, y = camera.world_to_screen(self.x, self.y)

        pygame.draw.circle(screen, color_tuple, (x, y), self.radius)

class EnemySpawner:

    def __init__(self):
        self.enemy_types = {
            "minion": {"size": 15, "hp": 1, "damage": 1, "speed": 0.3, "treasure_drop": 5}, 
            "tank": {"size": 25, "hp": 1, "damage": 2, "speed": 0.1, "treasure_drop": 20}, 
            "giant": {"size": 45, "hp": 1, "damage": 3, "speed": 0.05, "treasure_drop": 50},
            "boss": {"size": 80, "hp": 300, "damage": 5, "speed": 0.15, "projectile_radius": 20, "treasure_drop": 1000}
            }

    def random_enemy_type(self):

        num = random.randint(1,10)

        if num <= 6:
            return list(self.enemy_types.items())[0]
        
        elif num <= 9:
            return list(self.enemy_types.items())[1]
        
        else:
            return list(self.enemy_types.items())[2]


    def get_spawn_position(self, player_x, player_y, enemy_size, room):

        while True:

            enemy_x = random.randint(int(room.left), int(room.right - enemy_size))
            enemy_y = random.randint(int(room.top), int(room.bottom - enemy_size))

            if ((enemy_x - player_x) ** 2 + (enemy_y - player_y) ** 2) ** 0.5 >= 100:
                return enemy_x, enemy_y
            
    def spawn(self, enemy_type, enemy_x, enemy_y, room, EnemyClass):

        return EnemyClass(enemy_x, enemy_y, self.enemy_types[enemy_type]["size"], self.enemy_types[enemy_type]["hp"], self.enemy_types[enemy_type]["damage"], self.enemy_types[enemy_type]["speed"], room, enemy_type, self.enemy_types[enemy_type]["treasure_drop"])
    

    def boss_spawn(self, enemy_type, enemy_x, enemy_y, room, BossClass):

        return BossClass(enemy_x, enemy_y, self.enemy_types[enemy_type]["size"], self.enemy_types[enemy_type]["hp"], self.enemy_types[enemy_type]["damage"], self.enemy_types[enemy_type]["speed"], room, enemy_type, self.enemy_types[enemy_type]["treasure_drop"], self.enemy_types[enemy_type]["projectile_radius"])       

class Enemy:
    def __init__(self, x, y, size, hp, collide_damage, speed, start_room, type, treasure_drop):
        #uses center coordinates

        #top-level info
        self.type = type
        self.treasure_drop = treasure_drop
        self.start_room = start_room
        self.alive = True
        self.kb_time = 0

        #positions
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y

        #size and speed
        self.size = size
        self.speed = speed

        #HP and damage
        self.hp = hp
        self.max_hp = hp
        self.collide_damage = collide_damage

        self.update_hitbox()

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

    def start_knockback(self, dx, dy, kb_speed):
        self.vx = dx * kb_speed
        self.vy = dy * kb_speed
        self.kb_speed = kb_speed
        self.kb_time = 20
        self.kb_time_original = self.kb_time

    def update_knockback(self, vx, vy):
        self.x += vx * self.kb_time / self.kb_time_original
        self.y += vy * self.kb_time / self.kb_time_original
        self.kb_time -= 1

    def update_hitbox(self):
        self.hitbox = pygame.Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)

    def draw(self, screen, color_tuple, camera: Camera):
        x, y = camera.world_to_screen(self.x - self.size/2, self.y - self.size/2)
        pygame.draw.rect(screen, color_tuple, (x, y, self.size, self.size))

    def draw_HP_bar(self, screen, camera: Camera):
        x, y = camera.world_to_screen(self.x - self.size/2, self.y - self.size/2 - 10)
        #red hitbox
        pygame.draw.rect(screen, (255,0,0), (x, y, self.size, 7))
        #Green hitbox
        pygame.draw.rect(screen, (0,255,0), (x, y, self.size * (self.hp / self.max_hp), 7))

    def take_damage(self, damage):
        self.damage = damage
        self.hp -= self.damage
        if self.hp <= 0:
            self.alive = False

    def death_treasure(self):
        
        return Coin(self.x, self.y, 'gold coins', self.treasure_drop)

class Player:
    def __init__(self, x, y, size, speed, hp):
        self.x = x
        self.y = y
        self.old_x = x
        self.old_y = y
        self.size = size
        self.speed = speed
        self.hp = hp
        self.max_hp = hp
        self.alive = True
        self.kb_time = 0

        self.update_hitbox()

        self.last_shot_time = 0

    def move(self, keys):

        if keys[pygame.K_w]:
            self.y -= self.speed

        if keys[pygame.K_s]:
            self.y += self.speed

        if keys[pygame.K_a]:
            self.x -= self.speed

        if keys[pygame.K_d]:
            self.x += self.speed

    def move_back_after_hit_wall(self):
        self.x = self.old_x
        self.y = self.old_y

    def start_knockback(self, dx, dy, kb_speed):
        self.vx = dx * kb_speed
        self.vy = dy * kb_speed
        self.kb_speed = kb_speed
        self.kb_time = 20
        self.kb_time_original = self.kb_time

    def update_knockback(self, vx, vy):
        self.x += vx * self.kb_time / self.kb_time_original
        self.y += vy * self.kb_time / self.kb_time_original
        self.kb_time -= 1

    def update_hitbox(self):
        self.hitbox = pygame.Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)

    def draw_HP_bar(self, screen, camera: Camera):
        x, y = camera.world_to_screen(self.x - self.size/2, self.y - self.size/2 - 10)
        #red hitbox
        pygame.draw.rect(screen, (255,0,0), (x, y, self.size, 7))
        #Green hitbox
        pygame.draw.rect(screen, (0,255,0), (x, y, self.size * (self.hp / self.max_hp), 7))

    def draw(self, screen, color_tuple, camera: Camera): 
        #render
        x, y = camera.world_to_screen(self.x - self.size/2, self.y - self.size/2)
        pygame.draw.rect(screen, color_tuple, (x, y, self.size, self.size))

    def take_damage(self, damage):
        self.damage = damage
        self.hp -= self.damage

        if self.hp <= 0:
            self.alive = False

    def can_fire(self):
        self.current_time = pygame.time.get_ticks()

        return self.current_time - self.last_shot_time >= 125

class Boss:
    def __init__(self, x, y, size, hp, collide_damage, speed, start_room, type, treasure_drop, projectile_radius):
        #uses center coordinates

        #TOP-LEVEL INFO

        #states
        self.possible_states = ["walking", "aiming", "charging", "firing", "knocked back"]
        self.state_progression = ["walking", "aiming", "firing", "walking", "aiming", "charging"]
        self.state_index = 0
        self.state = self.state_progression[self.state_index]
        self.state_duration = 200

        self.type = type
        self.treasure_drop = treasure_drop
        self.start_room = start_room
        self.kb_time = 0
        self.alive = True
        self.boss_spawned = False
        self.aimed = False
        self.fired = False

        #positions
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y

        #sizes
        self.size = size
        self.projectile_radius = projectile_radius

        #speed
        self.speed = speed
        self.charge_speed = 7
        self.projectile_speed = 3

        #HP and dmg
        self.hp = hp
        self.max_hp = hp
        self.collide_damage = collide_damage

        self.update_hitbox()

    def state_switch(self):
        if self.state_index == len(self.state_progression) - 1:
            self.state_index = 0
            self.state = self.state_progression[self.state_index]
            self.fired = False
            self.aimed = False
            
        else:
            self.state = self.state_progression[self.state_index + 1]
            self.state_index += 1

        self.state_duration = 200

    def state_countdown(self):
        self.state_duration -= 1

    def walk(self, px, py):
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

    def start_knockback(self, dx, dy, kb_speed):
        self.vx = dx * kb_speed
        self.vy = dy * kb_speed
        self.kb_speed = kb_speed
        self.kb_time = 20
        self.kb_time_original = self.kb_time

    def update_knockback(self, vx, vy):
        self.x += vx * self.kb_time / self.kb_time_original
        self.y += vy * self.kb_time / self.kb_time_original
        self.kb_time -= 1

    def update_hitbox(self):
        self.hitbox = pygame.Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)

    def draw(self, screen, color_tuple, camera: Camera):
        x, y = camera.world_to_screen(self.x - self.size/2, self.y - self.size/2)
        pygame.draw.rect(screen, color_tuple, (x, y, self.size, self.size))

    def draw_HP_bar(self, screen, camera: Camera):
        x, y = camera.world_to_screen(self.x - self.size/2, self.y - self.size/2 - 10)
        #red hitbox
        pygame.draw.rect(screen, (255,0,0), (x, y, self.size, 7))
        #Green hitbox
        pygame.draw.rect(screen, (0,255,0), (x, y, self.size * (self.hp / self.max_hp), 7))

    def take_damage(self, damage):
        self.damage = damage
        self.hp -= self.damage
        if self.hp <= 0:
            self.alive = False

    def death_treasure(self):
        
        return Coin(self.x, self.y, 'gold coins', self.treasure_drop)

game = Game()
game.run()