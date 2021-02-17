
class Cell:

    def __init__(self, row, col, isObstacle=False):
        self.row = row
        self.col = col
        self.isObstacle = isObstacle
        self.isExplored = False
        self.canCalibrate = False
