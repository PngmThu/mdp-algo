import enum


class Action(enum.Enum):
    MOVE_FORWARD = 'F'
    MOVE_BACKWARD = 'B'
    TURN_LEFT = 'L'
    TURN_RIGHT = 'R'
    TURN_LEFT_NO_CALIBRATE = 'LNC'
    TURN_RIGHT_NO_CALIBRATE = 'RNC'
    CALIBRATE = 'C'
    RIGHT_CALIBRATE = 'RC'
