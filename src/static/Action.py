import enum


class Action(enum.Enum):
    MOVE_FORWARD = 'F'
    MOVE_BACKWARD = 'B'
    TURN_LEFT = 'L'
    TURN_RIGHT = 'R'
    CALIBRATE = 'C'
