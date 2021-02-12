from ..static.Direction import Direction


# Up, right, down, left: 0, 1, 2, 3
di = [-1, 0, 1, 0]
dj = [0, 1, 0, -1]

# Relative position
# Top left, top, top right, right, bottom right, bottom, bottom left, left: 0, 1, 2, 3, 4, 5, 6, 7
offsetRow = [-1, -1, -1, 0, 1, 1, 1, 0]
offsetCol = [-1, 0, 1, 1, 1, 0, -1, -1]

# Maze
ROW_SIZE = 20
COL_SIZE = 15
START_ROW = 18
START_COL = 1
GOAL_ROW = 1
GOAL_COL = 13

# Robot
START_DIR = Direction.RIGHT
INF_COST = 999999
MOVE_COST = 10
TURN_COST = 20

# Sensor
SR_SENSOR_LOWER = 1
SR_SENSOR_UPPER = 4
LR_SENSOR_LOWER = 2
LR_SENSOR_UPPER = 6

# Simulator
CANVAS_HEIGHT = 700
CANVAS_WIDTH = 600
START_X = 50
START_Y = 50
GRID_WIDTH = 30

# 0: empty cell (white)
# 1: obstacle (blue)
# 2: start & goal zone (green)
# 3: robot (yellow)
# 4: facing direction of robot (orange)
colors = ['white', 'blue', 'green', 'yellow', 'orange', 'pink', 'grey']
