from states.base_state import BaseState

class StateManager:
    def __init__(self):
        self.current_state: BaseState = None
        self.pending_state: BaseState = None

    def change_state(self, state: BaseState):
        self.pending_state = state

    def update(self):
        if self.pending_state:
            self.current_state = self.pending_state
            self.pending_state = None
        self.current_state.update()

    def draw(self):
        self.current_state.draw()




        
        