from ..communication.CommManager import CommManager
from ..communication.CommandType import CommandType
from ..static.Action import Action
from ..static.Color import Color
from ..static.Constants import di, dj, MAX_FORWARD
from ..static.Direction import Direction
from ..utils.Helper import Helper


class ExplorationAlgo:

    def __init__(self, exploredMaze, realMaze, robot, simulator, timeLimit, realRun):
        self.exploredMaze = exploredMaze
        self.realMaze = realMaze
        self.robot = robot
        self.timeLimit = timeLimit
        self.startTime = None
        self.endTime = None
        self.simulator = simulator
        self.realRun = realRun

    """
    Determines the next move for the robot and executes it accordingly.
    For left hugging, look left first to always have obstacle at the right side
    """
    def nextMove(self):
        if self.lookLeft():
            self.moveRobot(Action.TURN_LEFT)
            if self.lookForward():
                # self.moveRobot(Action.MOVE_FORWARD)
                self.moveRobotForwardMultiple()
        elif self.lookForward():
            # self.moveRobot(Action.MOVE_FORWARD)
            self.moveRobotForwardMultiple()
        elif self.lookRight():
            self.moveRobot(Action.TURN_RIGHT)
            if self.lookForward():
                # self.moveRobot(Action.MOVE_FORWARD)
                self.moveRobotForwardMultiple()
        else:
            self.moveRobot(Action.TURN_RIGHT)
            self.moveRobot(Action.TURN_RIGHT)

    def moveRobot(self, action, exploredImages=None):
        if self.simulator is not None:
            self.simulator.updateRobotPos(action)
        self.robot.move(action, sendMsg=self.realRun)
        self.senseAndRepaint(exploredImages)

    def moveRobotForwardMultiple(self, exploredImages=None):
        numOfMoves = self.maxMoveForward()
        # print("numOfMoves:", numOfMoves)
        if numOfMoves == 1:
            self.robot.move(Action.MOVE_FORWARD, sendMsg=self.realRun)
            self.senseAndRepaint(exploredImages)
            return
        if self.realRun:
            CommManager.sendMsg(CommandType.MOVE_FORWARD, numOfMoves)
        while numOfMoves != 0:
            if self.simulator is not None:
                self.simulator.updateRobotPos(Action.MOVE_FORWARD)
            self.robot.move(Action.MOVE_FORWARD, sendMsg=False)
            self.senseAndRepaint(exploredImages)
            numOfMoves -= 1
        # if self.simulator is not None:
        #     self.simulator.updateRobotPos(action)
        # self.robot.move(action, sendMsg=self.realRun)
        # self.senseAndRepaint(exploredImages)

    def senseAndRepaint(self, exploredImages=None):
        self.robot.updateSensorsPos()
        sensorResults = self.robot.sense(self.exploredMaze, self.realMaze, exploredImages)
        sensors = [self.robot.SRFrontLeft, self.robot.SRFrontCenter, self.robot.SRFrontRight,
                   self.robot.SRLeftHead, self.robot.SRLeftTail, self.robot.LRRight]
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

    def maxMoveForward(self):
        maxMove = 0
        for n in range(4, 0, -1):
            offset = 4 - n
            if self.robot.curDir == Direction.UP:
                row = self.robot.curRow + 2 - offset
                col = self.robot.curCol - 2
                if Helper.isBoundary(row, col) or (
                        Helper.isValidCoordinates(row, col) and self.exploredMaze[row][col].isExplored and
                        self.exploredMaze[row][col].isObstacle):
                    maxMove = n
                    break
            elif self.robot.curDir == Direction.RIGHT:
                row = self.robot.curRow + 2
                col = self.robot.curCol + 2 - offset
                if Helper.isBoundary(row, col) or (
                        Helper.isValidCoordinates(row, col) and self.exploredMaze[row][col].isExplored and
                        self.exploredMaze[row][col].isObstacle):
                    maxMove = n
                    break
            elif self.robot.curDir == Direction.DOWN:
                row = self.robot.curRow - 2 + offset
                col = self.robot.curCol + 2
                if Helper.isBoundary(row, col) or (
                        Helper.isValidCoordinates(row, col) and self.exploredMaze[row][col].isExplored and
                        self.exploredMaze[row][col].isObstacle):
                    maxMove = n
                    break
            elif self.robot.curDir == Direction.LEFT:
                row = self.robot.curRow - 2
                col = self.robot.curCol - 2 + offset
                if Helper.isBoundary(row, col) or (
                        Helper.isValidCoordinates(row, col) and self.exploredMaze[row][col].isExplored and
                        self.exploredMaze[row][col].isObstacle):
                    maxMove = n
                    break
        # print("maxMove:", maxMove)
        for n in range(maxMove, 0, -1):
            row = self.robot.curRow + di[self.robot.curDir.value] * n
            col = self.robot.curCol + dj[self.robot.curDir.value] * n
            if self.canVisit(row, col):
                return n
        return 0

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
