import time

from .ExplorationAlgo import ExplorationAlgo
from .FastestPath import FastestPath
from ..static.Constants import ROW_SIZE, COL_SIZE, START_ROW, START_COL, \
    GOAL_ROW, GOAL_COL
from ..static.Direction import Direction
from ..utils.Helper import Helper


# Inherit from ExplorationAlgo
class Exploration(ExplorationAlgo):

    def __init__(self, exploredMaze, realMaze, robot, simulator, timeLimit, coverageLimit):
        super().__init__(exploredMaze, realMaze, robot, simulator, timeLimit)
        self.coverageLimit = coverageLimit
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

    def calculateExploredCount(self):
        cnt = 0
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                if self.exploredMaze[i][j].isExplored:
                    cnt += 1
        print("Explored count:", cnt)
        return cnt

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
