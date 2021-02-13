from ..static.Action import Action
from ..static.Color import Color
from ..static.Constants import di, dj
from ..utils.Helper import Helper


class ExplorationAlgo:

    def __init__(self, exploredMaze, realMaze, robot, simulator, timeLimit):
        self.exploredMaze = exploredMaze
        self.realMaze = realMaze
        self.robot = robot
        self.timeLimit = timeLimit
        self.startTime = None
        self.endTime = None
        self.simulator = simulator

    """
    Determines the next move for the robot and executes it accordingly.
    For right hugging, look right first to always have obstacle at the right side
    """
    def nextMove(self):
        if self.lookRight():
            self.moveRobot(Action.TURN_RIGHT)
            if self.lookForward():
                self.moveRobot(Action.MOVE_FORWARD)
        elif self.lookForward():
            self.moveRobot(Action.MOVE_FORWARD)
        elif self.lookLeft():
            self.moveRobot(Action.TURN_LEFT)
            if self.lookForward():
                self.moveRobot(Action.MOVE_FORWARD)
        else:
            self.moveRobot(Action.TURN_RIGHT)
            self.moveRobot(Action.TURN_RIGHT)

    def moveRobot(self, action):
        if self.simulator is not None:
            self.simulator.updateRobotPos(action)
        self.robot.move(action)
        self.senseAndRepaint()

    def senseAndRepaint(self):
        self.robot.updateSensorsPos()
        sensorResults = self.robot.sense(self.exploredMaze, self.realMaze)
        sensors = [self.robot.SRFrontLeft, self.robot.SRFrontCenter, self.robot.SRFrontRight,
                   self.robot.SRRight, self.robot.SRLeft, self.robot.LRLeft]
        if self.simulator is None:
            return
        # Repaint in simulator
        for i in range(len(sensors)):
            dist = sensorResults[i]
            sensor = sensors[i]
            if dist == -1:
                for d in range(1, sensor.upperRange + 1):
                    self.simulator.paintCell(sensor.curRow + d * di[sensor.curDir.value], sensor.curCol + d * dj[sensor.curDir.value], Color.EMPTY_CELL)
            else:
                for d in range(1, dist):
                    self.simulator.paintCell(sensor.curRow + d * di[sensor.curDir.value], sensor.curCol + d * dj[sensor.curDir.value], Color.EMPTY_CELL)
                if Helper.isValidCoordinates(sensor.curRow + dist * di[sensor.curDir.value], sensor.curCol + dist * dj[sensor.curDir.value]):
                    self.simulator.paintCell(sensor.curRow + dist * di[sensor.curDir.value], sensor.curCol + dist * dj[sensor.curDir.value], Color.OBSTACLE)

    def lookForward(self):
        return self.freeAt(self.robot.curDir)

    def lookRight(self):
        return self.freeAt(Helper.nextDir(self.robot.curDir))

    def lookLeft(self):
        return self.freeAt(Helper.previousDir(self.robot.curDir))

    # Check whether the next cell at the direction is free
    def freeAt(self, direction):
        row = self.robot.curRow + di[direction.value]
        col = self.robot.curCol + dj[direction.value]
        return self.canVisit(row, col)

    def canVisit(self, row, col):
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                r = row + dr
                c = col + dc
                if not Helper.isValidCoordinates(r, c) or not self.exploredMaze[r][c].isExplored or \
                        self.exploredMaze[r][c].isObstacle:
                    return False
        return True
