from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.game import Game

class Movement:
    def __init__(self, game: Game):
        self.game = game

    def update_entities(self):
        #player
        self.game.player.old_x = self.game.player.x
        self.game.player.old_y = self.game.player.y

        self.game.player.move(self.game.keys)

        self.game.player.update_hitbox()

        #enemy
        for enemy in self.game.enemies:
            if enemy.start_room.room_field.contains(self.game.player.hitbox):
                enemy.move(self.game.player.x, self.game.player.y)

                if enemy.kb_time > 0:
                    enemy.update_knockback(enemy.vx, enemy.vy)
            else:
                enemy.return_to_start()

            enemy.update_hitbox()
            enemy.domain_restriction()

    def handle_wall_collisions(self, extra_rooms=None):
        rooms = list(self.game.rooms)
        if extra_rooms:
            rooms.extend([extra_rooms])
        for room in rooms:
            for hitbox in room.wall_hitboxes.values():
                if hitbox:
                    for segment in hitbox:
                        if self.game.player.hitbox.colliderect(segment):
                            self.push_out_of_rect(self.game.player, segment)
        self.game.player.update_hitbox()

    def push_out_of_rect(self, entity, rect):
        """Push an entity out of a wall rect on the shortest-overlap axis."""
        past_left_edge = entity.hitbox.right - rect.left   # player's right edge past wall's left
        past_right_edge = rect.right - entity.hitbox.left  # player's left edge past wall's right
        past_top_edge = entity.hitbox.bottom - rect.top    # player's bottom past wall's top
        past_bottom_edge = rect.bottom - entity.hitbox.top # player's top past wall's bottom

        min_x = min(past_left_edge, past_right_edge)
        min_y = min(past_top_edge, past_bottom_edge)

        if min_x < min_y:
            # push out on X axis
            if past_left_edge < past_right_edge:
                entity.x -= past_left_edge
            else:
                entity.x += past_right_edge
        elif min_x > min_y:
            # push out on Y axis
            if past_top_edge < past_bottom_edge:
                entity.y -= past_top_edge
            else:
                entity.y += past_bottom_edge

        else:
            if past_left_edge < past_right_edge:
                entity.x -= past_left_edge
            else:
                entity.x += past_right_edge

            if past_top_edge < past_bottom_edge:
                entity.y -= past_top_edge
            else:
                entity.y += past_bottom_edge

    def push_into_rect(self, entity, rect):
        """Push an entity so their hitbox is fully inside rect (e.g. room bounds)."""
        if entity.hitbox.left < rect.left:
            entity.x += rect.left - entity.hitbox.left
        elif entity.hitbox.right > rect.right:
            entity.x -= entity.hitbox.right - rect.right
        if entity.hitbox.top < rect.top:
            entity.y += rect.top - entity.hitbox.top
        elif entity.hitbox.bottom > rect.bottom:
            entity.y -= entity.hitbox.bottom - rect.bottom




                

    
