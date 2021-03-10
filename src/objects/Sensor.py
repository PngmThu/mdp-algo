from ..static.Constants import di, dj
from ..utils.Helper import Helper


class Sensor:

    def __init__(self, lowerRange, upperRange, id):
        self.lowerRange = lowerRange
        self.upperRange = upperRange
        self.curRow = None
        self.curCol = None
        self.curDir = None
        self.id = id

    def setPos(self, row, col, direction):
        self.curRow = row
        self.curCol = col
        self.curDir = direction

    """
    Return the distance to the nearest obstacle or -1 if no obstacle is detected
    > exploredMaze: the maze that is being explored
    > realMaze: the real maze that should be the result after exploration
    """
    def sense(self, exploredMaze, realMaze):
        dr = di[self.curDir.value]
        dc = dj[self.curDir.value]

        # If there is obstacle in the blind range of the sensor
        # Return the distance so as to not continue to check the upper range
        if self.lowerRange > 1:
            for dist in range(self.lowerRange):
                row = self.curRow + dr * dist
                col = self.curCol + dc * dist
                # Boundary wall
                if not Helper.isValidCoordinates(row, col):
                    return dist
                # Obstacle
                if realMaze[row][col].isObstacle:
                    return dist

        # Check [lowerRange, upperRange]
        for dist in range(self.lowerRange, self.upperRange + 1):
            row = self.curRow + dr * dist
            col = self.curCol + dc * dist

            # Boundary wall
            if not Helper.isValidCoordinates(row, col):
                return dist

            # Explored
            exploredMaze[row][col].isExplored = True

            # Explored cell is an obstacle
            if realMaze[row][col].isObstacle and not Helper.inStartZone(row, col) and not Helper.inGoalZone(row, col):
                exploredMaze[row][col].isObstacle = True
                return dist

        # No obstacle is detected
        return -1

    def processSensorVal(self, exploredMaze, sensorVal):
        if sensorVal == 0:
            return

        dr = di[self.curDir.value]
        dc = dj[self.curDir.value]

        # If there is obstacle in the blind range of the sensor
        # Return so as to not continue to check the upper range
        if self.lowerRange > 1:
            for dist in range(self.lowerRange):
                row = self.curRow + dr * dist
                col = self.curCol + dc * dist
                # Boundary wall
                if not Helper.isValidCoordinates(row, col):
                    return
                # Obstacle
                if exploredMaze[row][col].isObstacle:
                    return

        # Check [lowerRange, upperRange]
        for dist in range(self.lowerRange, self.upperRange + 1):
            row = self.curRow + dr * dist
            col = self.curCol + dc * dist

            # Boundary wall
            if not Helper.isValidCoordinates(row, col):
                return

            # Explored
            exploredMaze[row][col].isExplored = True
            exploredMaze[row][col].isObstacle = False

            # Explored cell is an obstacle
            if sensorVal == dist and not Helper.inStartZone(row, col) and not Helper.inGoalZone(row, col):
                exploredMaze[row][col].isObstacle = True
                break
