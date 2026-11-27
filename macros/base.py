from enum import Enum, auto
import time

class State(Enum):
    UNKNOWN = auto()
    LOADING = auto()
    MENU = auto()
    DIALOGUE = auto()
    POPUP = auto()

class BaseMacro:
    def __init__(self, vision, inputs):
        self.vision = vision
        self.inputs = inputs
        self.prev_action_time = time.time()
    
    def check_state(self, rect) -> State:
        if 
        # check pixels