from __future__ import annotations
from typing import TYPE_CHECKING
from core.utility import get_direction

if TYPE_CHECKING:
    from core.game import Game

class Combat:
    def __init__(self, game: Game):
        self.game = game
        self.player = self.game.player

    def handle_projectiles(self):
        for projectile in self.game.projectiles[:]:
            projectile.update_projectile()
            projectile.update_hitbox()

            if projectile not in self.game.projectiles:
                continue

            hit = False

            if projectile.owner == "player":
                for enemy in self.game.enemies:
                    if projectile.hitbox.colliderect(enemy.hitbox):
                        enemy.take_damage(1)
                        self.game.projectiles.remove(projectile)
                        hit = True
                        break

                if not hit and self.game.boss and projectile.hitbox.colliderect(self.game.boss.hitbox):
                    self.game.boss.take_damage(1)
                    self.game.projectiles.remove(projectile)
                    hit = True

            elif projectile.owner in ["enemy", "boss"]:
                if projectile.hitbox.colliderect(self.player.hitbox):
                    self.player.take_damage(1)
                    self.game.projectiles.remove(projectile)
                    hit = True

            # wall collisions
            if not hit:
                for room in self.game.rooms:
                    for hitbox in room.wall_hitboxes.values():
                        if hitbox:
                            for segment in hitbox:
                                if segment.colliderect(projectile.hitbox):
                                    self.game.projectiles.remove(projectile)
                                    hit = True
                                    break
                        if hit:
                            break
                    if hit:
                        break

    def start_knockback(self):
        for enemy in self.game.enemies:
            if enemy.hitbox.colliderect(self.player.hitbox):
                player_dx, player_dy, enemy_dx, enemy_dy = (-d for d in get_direction(self.player, enemy))

                enemy.start_knockback(enemy_dx, enemy_dy, enemy.kb_speed)
                self.player.start_knockback(player_dx, player_dy, self.player.kb_speed)

                self.player.take_damage(enemy.collide_damage)
        
        if self.game.boss and self.game.boss.hitbox.colliderect(self.player.hitbox):
            player_dx, player_dy, boss_dx, boss_dy = (-d for d in get_direction(self.player, self.game.boss))

            self.game.boss.start_knockback(boss_dx, boss_dy, self.game.boss.kb_speed)
            self.player.start_knockback(player_dx, player_dy, self.player.kb_speed)

            self.player.take_damage(self.game.boss.collide_damage)

    def update_knockback(self):
        if self.player.kb_time > 0:
            self.player.update_knockback(self.player.vx, self.player.vy)

        for enemy in self.game.enemies:
            if enemy.kb_time > 0:
                enemy.update_knockback(enemy.vx, enemy.vy)

        if self.game.boss and self.game.boss.kb_time > 0:
            self.game.boss.update_knockback(self.game.boss.vx, self.game.boss.vy)

    def handle_deaths(self):
        for enemy in self.game.enemies[:]:
            if not enemy.alive:
                self.game.enemies.remove(enemy)
                self.game.treasures.append(enemy.death_treasure())

        if self.game.boss:
            if not self.game.boss.alive:
                self.game.boss = None
