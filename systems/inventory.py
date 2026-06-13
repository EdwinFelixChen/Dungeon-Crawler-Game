from __future__ import annotations
from typing import TYPE_CHECKING
from core.utility import get_direction

if TYPE_CHECKING:
    from core.game import Game

class Inventory:
    def __init__(self, game: Game):
        self.game = game
        self.inventory = {}

    def add_to_inventory(self, item, quantity=None, description=None):
        if item not in self.inventory:
            self.inventory[item] = {"quantity": quantity, "description": description}

        else:
            self.inventory[item]['quantity'] += quantity

    def access_inventory(self, draw_sprite):
        draw_sprite()
