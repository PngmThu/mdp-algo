import time

from .ExplorationAlgo import ExplorationAlgo
from .FastestPath import FastestPath
from ..communication.CommManager import CommManager
from ..communication.CommandType import CommandType
from ..static.Action import Action
from ..static.Constants import ROW_SIZE, COL_SIZE, START_ROW, START_COL, \
    GOAL_ROW, GOAL_COL
from ..static.Direction import Direction
from ..utils.Helper import Helper


# Inherit from ExplorationAlgo
class Exploration(ExplorationAlgo):

    def __init__(self, exploredMaze, realMaze, robot, simulator, timeLimit, coverageLimit, realRun):
        super().__init__(exploredMaze, realMaze, robot, simulator, timeLimit, realRun)
        self.coverageLimit = coverageLimit
        self.timeLeftToGoHome = 90
        self.resetUnexploredMarkCount = 0

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

        # TO DO: Initial Calibration

        self.senseAndRepaint()

        self.nextMove()
        exploredCount = self.calculateExploredCount()
        while exploredCount < self.coverageLimit and time.time() < self.endTime - self.timeLeftToGoHome:
            if (exploredCount > self.coverageLimit / 2) and self.robot.curRow == START_ROW and self.robot.curCol == START_COL:
                break

            self.nextMove()
            exploredCount = self.calculateExploredCount()

        # If exceed time limit, terminate
        if time.time() >= self.endTime:
            return

        # Continue exploring when there are unexplored areas although robot has returned to start zone
        exploredCount = self.calculateExploredCount()
        # exploredMarkCount = self.calculateExploredMarkCount()
        # while exploredMarkCount < self.coverageLimit and exploredCount < self.coverageLimit and time.time() < self.endTime - self.timeLeftToGoHome:
        while self.resetUnexploredMarkCount < 10 and exploredCount < self.coverageLimit and time.time() < self.endTime - self.timeLeftToGoHome:
            self.fastestPathToUnexplored()
            exploredCount = self.calculateExploredCount()
            # exploredMarkCount = self.calculateExploredMarkCount()

        self.goHome()
        if self.realRun:
            CommManager.sendMsg(CommandType.FINISH)

    def calculateExploredCount(self):
        cnt = 0
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                if self.exploredMaze[i][j].isExplored:
                    cnt += 1
        # print("Explored count:", cnt)
        return cnt

    def calculateExploredMarkCount(self):
        cnt = 0
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                if self.exploredMaze[i][j].exploredMark:
                    cnt += 1
        return cnt

    def goHome(self):
        # Go to goal if never touched goal and then go back to start
        CommManager.sendMsg(CommandType.FP_START_TO_ARDUINO)
        if not self.robot.touchedGoal and time.time() < self.endTime:
            actions = FastestPath(self.exploredMaze, self.robot, GOAL_ROW, GOAL_COL, self.realRun).runFastestPath(execute=False)
            self.executeFastestPath(actions, goToHome=True)
        # Go back start
        actions = FastestPath(self.exploredMaze, self.robot, START_ROW, START_COL, self.realRun).runFastestPath(execute=False)
        self.executeFastestPath(actions, goToHome=True)

        print("Exploration complete!")
        exploredCount = self.calculateExploredCount()
        print("Final explored count:", exploredCount)
        print("Time:", time.time() - self.startTime, "seconds")

        # TO DO: Calibrate to make sure that the robot is entirely inside start zone

    def fastestPathToUnexplored(self):
        unexploredCell = self.findFirstUnexploredCell()
        # self.printExploredMark()
        # When no more unexploredMark cell
        if unexploredCell == -1:
            if self.resetUnexploredMarkCount < 10:
                self.resetUnexploredMark()
                self.resetUnexploredMarkCount += 1
            print("resetUnexploredMarkCount:", self.resetUnexploredMarkCount)
            if self.resetUnexploredMarkCount >= 10:
                self.setAllUnexploredMark()
            return
        row, col = unexploredCell
        res = self.findNeighborOfUnexploredCell(row, col)
        self.exploredMaze[row][col].exploredMark = True
        if res == -1:
            return
        targetRow, targetCol = res
        # actions = FastestPath(self.exploredMaze, self.robot, targetRow, targetCol, self.realRun).runFastestPath(
        #     execute=False)
        CommManager.sendMsg(CommandType.FP_START_TO_ARDUINO)
        actions = FastestPath(self.exploredMaze, self.robot, targetRow, targetCol, self.realRun).runFastestPath(execute=False)
        self.executeFastestPath(actions)
        # for action in actions:
        #     if time.time() >= self.endTime:
        #         break
        #     self.moveRobot(action)
        #     # Break if the cell is explored when moving
        #     if self.exploredMaze[row][col].isExplored:
        #         break

        if time.time() >= self.endTime:
            return

        CommManager.sendMsg(CommandType.EX_START_TO_ARDUINO)
        self.senseAndRepaint()
        # Only turn when the cell is not explored when moving
        if not self.exploredMaze[row][col].isExplored:
            curCell = self.exploredMaze[self.robot.curRow][self.robot.curCol]
            targetDir = Helper.getTargetDirForUnexplored(curCell, self.robot.curDir, self.exploredMaze[row][col])
            while self.robot.curDir != targetDir:
                targetAction = Helper.getTargetTurn(self.robot.curDir, targetDir)
                self.moveRobot(targetAction)
                curCell = self.exploredMaze[self.robot.curRow][self.robot.curCol]
                targetDir = Helper.getTargetDirForUnexplored(curCell, self.robot.curDir,
                                                             self.exploredMaze[row][col])

    def findFirstUnexploredCell(self):
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                if not self.exploredMaze[i][j].exploredMark:
                    print("in findFirstUnexploredCell:", i, j)
                    return i, j
        return -1

    def findNeighborOfUnexploredCell(self, row, col):
        direction = Direction.DOWN
        for i in range(4):
            r, c = Helper.neighborOfUnexploredCellAt(row, col, direction)
            # print(r, c)
            if direction == Direction.UP or direction == Direction.DOWN:
                for dc in range(-1, 2):
                    if self.canVisit(r, c + dc):
                        return r, c + dc
            else:
                for dr in range(-1, 2):
                    if self.canVisit(r + dr, c):
                        return r + dr, c
            direction = Helper.nextDir(direction)
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

    def executeFastestPath(self, actions, goToHome=False):
        # print("executeFastestPath")
        if not self.realRun:
            for action in actions:
                self.robot.move(action, sendMsg=False)
            return

        timeOffset = self.timeLeftToGoHome
        if goToHome:
            timeOffset = 0

        fCount = 0
        for i in range(len(actions)):
            if time.time() >= self.endTime - timeOffset:
                break
            action = actions[i]
            if action == Action.MOVE_FORWARD:
                fCount += 1
                if fCount == 2:
                    obstacleAvoid = False
                    self.robot.moveForwardMultiple(fCount, obstacleAvoid)
                    Helper.waitForCommand(CommandType.ACTION_COMPLETE)
                    # time.sleep(0.05)
                    fCount = 0
                    CommManager.sendMsg(CommandType.CALIBRATE)
                    Helper.waitForCommand(CommandType.ACTION_COMPLETE)
                    # time.sleep(0.05)
            else:
                if fCount > 0:
                    self.robot.moveForwardMultiple(fCount, obstacleAvoid=False)
                    Helper.waitForCommand(CommandType.ACTION_COMPLETE)
                    # time.sleep(0.05)
                    fCount = 0
                self.robot.move(action, sendMsg=True)
                Helper.waitForCommand(CommandType.ACTION_COMPLETE)
                time.sleep(0.05)

        if fCount > 0:
            obstacleAvoid = False
            self.robot.moveForwardMultiple(fCount, obstacleAvoid)
            Helper.waitForCommand(CommandType.ACTION_COMPLETE)
            # time.sleep(0.05)

    def resetUnexploredMark(self):
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                if self.exploredMaze[i][j].isExplored:
                    self.exploredMaze[i][j].exploredMark = True
                else:
                    self.exploredMaze[i][j].exploredMark = False

    def setAllUnexploredMark(self):
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                self.exploredMaze[i][j].exploredMark = True

    def printExploredMark(self):
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                if self.exploredMaze[i][j].exploredMark:
                    print("1", end=" ")
                else:
                    print("0", end=" ")
            print()
