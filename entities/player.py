import pygame
from entities.entity import Entity

class Player(Entity):
    def __init__(self, x, y, size, speed, kb_speed, hp):
        super().__init__(x, y, size, hp, max_hp=hp)
        self.speed = speed
        self.last_shot_time = 0
        self.kb_speed = kb_speed

    def move(self, keys):

        if keys[pygame.K_w]:
            self.y -= self.speed

        if keys[pygame.K_s]:
            self.y += self.speed

        if keys[pygame.K_a]:
            self.x -= self.speed

        if keys[pygame.K_d]:
            self.x += self.speed

    def can_fire(self):
        self.current_time = pygame.time.get_ticks()

        return self.current_time - self.last_shot_time >= 125