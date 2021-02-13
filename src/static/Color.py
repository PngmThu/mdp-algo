import enum


class Color(enum.Enum):
    EMPTY_CELL = 0
    OBSTACLE = 1
    START_ZONE = 2
    GOAL_ZONE = 2
    ROBOT = 3
    FACING = 4
    WAYPOINT = 5
    UNEXPLORED = 6
    IMAGE = 7
