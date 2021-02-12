import time

from .FastestPath import FastestPath
from ..static.Action import Action
from ..static.Constants import ROW_SIZE, COL_SIZE, di, dj, START_ROW, START_COL, \
    GOAL_ROW, GOAL_COL
from ..static.Direction import Direction
from ..utils.Helper import Helper


class Exploration:

    def __init__(self, exploredMaze, realMaze, robot, coverageLimit, timeLimit):
        self.exploredMaze = exploredMaze
        self.realMaze = realMaze
        self.robot = robot
        self.coverageLimit = coverageLimit
        self.timeLimit = timeLimit
        self.startTime = None
        self.endTime = None
        self.exploredCount = 18  # start and goal zone

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
        self.nextMove()
        exploredCount = self.calculateExploredCount()
        while exploredCount < self.coverageLimit and time.time() < self.endTime:
            if self.robot.curRow == START_ROW and self.robot.curCol == START_COL:
                break

            self.nextMove()
            exploredCount = self.calculateExploredCount()

        # TO DO: Continue exploring when there are unexplored areas although robot has returned to start zone

        #self.goHome()

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
        self.robot.move(action)
        self.senseAndRepaint()
        # TO DO: repaint simulator

    def senseAndRepaint(self):
        self.robot.updateSensorsPos()
        self.robot.sense(self.exploredMaze, self.realMaze)
        # TO DO: repaint simulator

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
                if not Helper.isValidCoordinates(r, c) or not self.exploredMaze[r][c].isExplored or self.exploredMaze[r][c].isObstacle:
                    return False
        return True

    def goHome(self):
        # Go to goal if never touched goal
        if not self.robot.touchedGoal and time.time() < self.endTime:
            actions = FastestPath(self.exploredMaze, self.robot, GOAL_ROW, GOAL_COL).runFastestPath()
            for action in actions:
                self.moveRobot(action)

        # Go back start
        actions = FastestPath(self.exploredMaze, self.robot, START_ROW, START_COL).runFastestPath()
        for action in actions:
            self.moveRobot(action)

        print("Exploration complete!")
        exploredCount = self.calculateExploredCount()
        print("Final explored count:", exploredCount)
        print("Time:", time.time() - self.startTime, "seconds")

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
