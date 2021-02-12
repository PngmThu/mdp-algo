import time

from .FastestPath import FastestPath
from ..static.Action import Action
from ..static.Color import Color
from ..static.Constants import ROW_SIZE, COL_SIZE, di, dj, START_ROW, START_COL, \
    GOAL_ROW, GOAL_COL
from ..static.Direction import Direction
from ..utils.Helper import Helper


class Exploration:

    def __init__(self, exploredMaze, realMaze, robot, simulator, coverageLimit, timeLimit):
        self.exploredMaze = exploredMaze
        self.realMaze = realMaze
        self.robot = robot
        self.coverageLimit = coverageLimit
        self.timeLimit = timeLimit
        self.startTime = None
        self.endTime = None
        self.exploredCount = 18  # start and goal zone
        self.simulator = simulator
        self.backToStart = False

    """
     Loops through robot movements until one (or more) of the following conditions is met:
     1. Robot is back to start
     2. areaExplored >= coverageLimit and System.currentTimeMillis() >= endTime
    """

    def runExploration(self):
        print("Start exploration...")

        # in seconds
        self.startTime = time.time()
        self.endTime = self.startTime + self.timeLimit

        self.senseAndRepaint()

        self.executeNextMove()
        # self.nextMove()
        # exploredCount = self.calculateExploredCount()
        # while exploredCount < self.coverageLimit and time.time() < self.endTime:
        #     if self.robot.curRow == START_ROW and self.robot.curCol == START_COL:
        #         break
        #
        #     self.nextMove()
        #     exploredCount = self.calculateExploredCount()

        # TO DO: Continue exploring when there are unexplored areas although robot has returned to start zone

        # self.goHome()

    def executeNextMove(self):
        self.nextMove()

        # if self.robot.curRow == START_ROW and self.robot.curCol == START_COL:
        #     return

        exploredCount = self.calculateExploredCount()
        if exploredCount < self.coverageLimit and time.time() < self.endTime:
            self.simulator.window.after(150, lambda: self.executeNextMove())
        else:
            self.printExploredMaze()
            self.goHome()

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
        self.simulator.updateRobotPos(action)

        self.robot.move(action)
        self.senseAndRepaint()

    def senseAndRepaint(self):
        self.robot.updateSensorsPos()
        sensorResults = self.robot.sense(self.exploredMaze, self.realMaze)
        sensors = [self.robot.SRFrontLeft, self.robot.SRFrontCenter, self.robot.SRFrontRight,
                   self.robot.SRRight, self.robot.SRLeft, self.robot.LRLeft]
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

    def calculateExploredCount(self):
        cnt = 0
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                if self.exploredMaze[i][j].isExplored:
                    cnt += 1
        print("Explored count:", cnt)
        return cnt

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

    def goHome(self):
        # Go to goal if never touched goal and then go back to start
        if not self.robot.touchedGoal and time.time() < self.endTime:
            actions = FastestPath(self.exploredMaze, self.robot, GOAL_ROW, GOAL_COL).runFastestPath()
            # for action in actions:
            #     self.moveRobot(action)
            self.executeAction(actions, 0)
        else:
            # Go back start
            actions = FastestPath(self.exploredMaze, self.robot, START_ROW, START_COL).runFastestPath()
            self.backToStart = True
            self.executeAction(actions, 0)
            # for action in actions:
            #     self.moveRobot(action)
            #
            # print("Exploration complete!")
            # exploredCount = self.calculateExploredCount()
            # print("Final explored count:", exploredCount)
            # print("Time:", time.time() - self.startTime, "seconds")

        # TO DO: Calibrate to make sure that the robot is entirely inside start zone

    def findFirstUnexploredCell(self):
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                if not self.exploredMaze[i][j].isExplored:
                    return i, j
        return -1

    def findNeighborOfUnexploredCell(self, row, col):
        up_r, up_c = Helper.neighborOfUnexploredCellAt(row, col, Direction.UP)
        down_r, down_c = Helper.neighborOfUnexploredCellAt(row, col, Direction.DOWN)
        left_r, left_c = Helper.neighborOfUnexploredCellAt(row, col, Direction.LEFT)
        right_r, right_c = Helper.neighborOfUnexploredCellAt(row, col, Direction.RIGHT)

        if self.canVisit(down_r, down_c):
            return down_r, down_c
        elif self.canVisit(left_r, left_c):
            return left_r, left_c
        elif self.canVisit(up_r, up_c):
            return up_r, up_c
        elif self.canVisit(right_r, right_c):
            return right_r, right_c
        else:
            return -1

    def printExploredMaze(self):
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                if self.exploredMaze[i][j].isExplored:
                    if self.exploredMaze[i][j].isObstacle:
                        print("1", end=" ")
                    else:
                        print("0", end=" ")
                else:
                    print("X", end=" ")
            print()

    def executeAction(self, actions, index):
        if index < len(actions):
            self.simulator.updateRobotPos(actions[index])
            self.robot.move(actions[index])
            if index + 1 < len(actions):
                self.simulator.window.after(150, lambda: self.executeAction(actions, index + 1))
            else:
                if not self.backToStart:
                    actions = FastestPath(self.exploredMaze, self.robot, START_ROW, START_COL).runFastestPath()
                    self.backToStart = True
                    self.executeAction(actions, 0)
                else:
                    print("Exploration complete!")
                    exploredCount = self.calculateExploredCount()
                    print("Final explored count:", exploredCount)
                    print("Time:", time.time() - self.startTime, "seconds")
