import pygame
from core.camera import Camera
from core.utility import get_direction

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