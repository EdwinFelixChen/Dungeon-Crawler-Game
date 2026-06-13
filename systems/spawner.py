from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.enemy import GroundEnemy
    from entities.boss import Boss

class EnemySpawner:

    def __init__(self):
        self.enemy_types = {
            "minion": {"size": 15, "hp": 5, "damage": 1, "speed": 0.3, "kb_speed": 1, "treasure_drop": 5}, 
            "tank": {"size": 25, "hp": 10, "damage": 2, "speed": 0.1, "kb_speed": 1, "treasure_drop": 20}, 
            "giant": {"size": 45, "hp": 20, "damage": 3, "speed": 0.05, "kb_speed": 1, "treasure_drop": 50},
            "boss": {"size": 80, "hp": 200, "damage": 5, "speed": 0.15, "kb_speed": 1, "projectile_radius": 20, "treasure_drop": 1000}
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
            
    def spawn(self, enemy_type, enemy_x, enemy_y, room, EnemyClass: GroundEnemy):

        return EnemyClass(
            enemy_x, 
            enemy_y, 
            self.enemy_types[enemy_type]["size"], 
            self.enemy_types[enemy_type]["hp"], 
            self.enemy_types[enemy_type]["damage"], 
            self.enemy_types[enemy_type]["speed"], 
            self.enemy_types[enemy_type]["kb_speed"], 
            room, 
            enemy_type, 
            self.enemy_types[enemy_type]["treasure_drop"]
        )
    
    def boss_spawn(self, enemy_type, enemy_x, enemy_y, room, BossClass: Boss):

        return BossClass(
            enemy_x, 
            enemy_y, 
            self.enemy_types[enemy_type]["size"], 
            self.enemy_types[enemy_type]["hp"], 
            self.enemy_types[enemy_type]["damage"], 
            self.enemy_types[enemy_type]["speed"], 
            self.enemy_types[enemy_type]["kb_speed"], 
            room, 
            enemy_type, 
            self.enemy_types[enemy_type]["treasure_drop"], 
            self.enemy_types[enemy_type]["projectile_radius"]
        )       
