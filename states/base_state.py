from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.game import Game


class BaseState:
    def __init__(self, game: Game):
        self.game = game

    def update(self):
        self.game.camera.update(self.game.player, self.game.screen_x, self.game.screen_y)

    def draw(self):
        pass

    def change_state(self):
        pass
