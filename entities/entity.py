import pygame
from core.camera import Camera

class Entity:
    def __init__(self, x, y, size, hp, max_hp):
        #uses center coordinates
        self.x = x
        self.y = y
        self.size = size
        self.hp = hp
        self.max_hp = max_hp
        self.alive = True
        self.kb_time = 0
        self.update_hitbox()

    def update_hitbox(self):
          self.hitbox = pygame.Rect(
              self.x - self.size/2, self.y - self.size/2, self.size, self.size
          )

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False

    def start_knockback(self, dx, dy, kb_speed):
        self.vx = dx * kb_speed
        self.vy = dy * kb_speed
        self.kb_speed = kb_speed
        self.kb_time = 25
        self.kb_time_original = self.kb_time

    def update_knockback(self, vx, vy):
        self.x += vx * self.kb_time / self.kb_time_original
        self.y += vy * self.kb_time / self.kb_time_original
        self.kb_time -= 1

    def draw(self, screen, color_tuple, camera: Camera):
          x, y = camera.world_to_screen(self.x - self.size/2, self.y - self.size/2)
          pygame.draw.rect(screen, color_tuple, (x, y, self.size, self.size))

    def draw_HP_bar(self, screen, camera: Camera):
        x, y = camera.world_to_screen(self.x - self.size/2, self.y - self.size/2 - 10)
        pygame.draw.rect(screen, (255,0,0), (x, y, self.size, 7))
        pygame.draw.rect(screen, (0,255,0), (x, y, self.size * (self.hp / self.max_hp), 7))
