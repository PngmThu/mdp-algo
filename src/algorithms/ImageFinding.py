import time

from .Exploration import Exploration
from .FastestPath import FastestPath
from ..communication.CommManager import CommManager
from ..communication.CommandType import CommandType
from ..static.Action import Action
from ..static.Constants import MAX_NUMBER_OF_IMAGES, START_ROW, START_COL, ROW_SIZE, COL_SIZE, di, dj, MAX_FORWARD
from ..static.Direction import Direction
from ..utils.Helper import Helper


# Inherit from Exploration
class ImageFinding(Exploration):

    # realImages: the set of (row, col, direction) of real images
    def __init__(self, exploredMaze, realMaze, robot, simulator, timeLimit, coverageLimit, realRun, realImages):
        super().__init__(exploredMaze, realMaze, robot, simulator, timeLimit, coverageLimit, realRun)
        self.exploredImages = set()
        self.realImages = realImages
        self.needHug = None
        self.backToStart = False
        # self.forwardCnt = 0

        self.records = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                self.records[i][j] = [0, 0, 0, 0]

        self.flipRecord = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)

    def runImageFinding(self):
        print("Start image finding...")

        # in seconds
        self.startTime = time.time()
        self.endTime = self.startTime + self.timeLimit

        self.senseAndRepaint(self.exploredImages, self.flipRecord)
        self.captureImage()

        self.nextMove()
        while len(self.exploredImages) < MAX_NUMBER_OF_IMAGES and time.time() < self.endTime:
            exploredCount = self.calculateExploredCount()
            if exploredCount < self.coverageLimit:
                if not self.backToStart:
                    self.nextMove()
                    if self.robot.curRow == START_ROW and self.robot.curCol == START_COL:
                        self.backToStart = True
                        print("back to start")
                else:
                    super().fastestPathToUnexplored()
            else:
                # Continue to hug wall until back to start
                if not self.backToStart:
                    self.nextMove()
                    if self.robot.curRow == START_ROW and self.robot.curCol == START_COL:
                        self.backToStart = True
                    continue

                if self.needHug is None:
                    self.initializeNeedHug()

                if not self.leftCellToHug():
                    break
                # Send FP_START to stop sending sensor data
                if self.realRun:
                    CommManager.sendMsg(CommandType.FP_START_TO_ARDUINO)

                startHugRow, startHugCol, startHugDir = self.goToCellToHug()
                if startHugRow is None or startHugCol is None or startHugDir is None:
                    break
                stopHugRow, stopHugCol, stopHugDir = self.getStopHugCell(startHugRow, startHugCol, startHugDir)
                self.nextMove(sense=False)
                self.updateNeedHug()
                while len(self.exploredImages) < MAX_NUMBER_OF_IMAGES and time.time() < self.endTime:
                    if self.robot.curRow == stopHugRow + di[stopHugDir.value] * 2 and self.robot.curCol == stopHugCol + \
                            dj[stopHugDir.value] * 2 and self.robot.curDir == Helper.previousDir(stopHugDir):
                        break
                    if self.robot.curRow == startHugRow + di[
                                                            startHugDir.value] * 2 and self.robot.curCol == startHugCol + dj[
                                                            startHugDir.value] * 2 and self.robot.curDir == Helper.previousDir(startHugDir):
                        break
                    self.nextMove(sense=False)
                    self.updateNeedHug()

        if self.realRun:
            CommManager.sendMsg(CommandType.FINISH)
        print("Done image finding!")
        print("Number of explored images:", len(self.exploredImages))
        print(self.exploredImages)

    """
        Determines the next move for the robot and executes it accordingly.
        For left hugging, look left first to always have obstacle at the right side
    """

    def nextMove(self, sense=True):
        if self.lookLeft():
            self.moveRobot(Action.TURN_LEFT, sense)
            if self.lookForward():
                self.moveRobot(Action.MOVE_FORWARD, sense)
        elif self.lookForward():
            self.moveRobot(Action.MOVE_FORWARD, sense)
        elif self.lookRight():
            self.moveRobot(Action.TURN_RIGHT, sense)
            if self.lookForward():
                self.moveRobot(Action.MOVE_FORWARD, sense)
        else:
            self.moveRobot(Action.TURN_RIGHT, sense)
            if self.lookForward():
                self.moveRobot(Action.MOVE_FORWARD, sense)
            else:
                self.moveRobot(Action.TURN_RIGHT, sense)

    def moveRobot(self, action, sense=True, exploredImages=None):
        # super().moveRobot(action, sense, exploredImages=self.exploredImages)
        if self.justCalibrate:
            if action == Action.TURN_RIGHT:
                self.robot.move(Action.TURN_RIGHT_NO_CALIBRATE, sendMsg=self.realRun)
            elif action == Action.TURN_LEFT:
                self.robot.move(Action.TURN_LEFT_NO_CALIBRATE, sendMsg=self.realRun)
            else:
                self.robot.move(action, sendMsg=self.realRun)
            self.justCalibrate = False
        else:
            self.robot.move(action, sendMsg=self.realRun)

        if sense:
            self.senseAndRepaint(self.exploredImages, self.flipRecord)
        elif self.realRun:
            # Helper.waitForCommand(CommandType.ACTION_COMPLETE)
            Helper.processCmdAndImage(CommandType.ACTION_COMPLETE, exploredImages, self.simulator)

        cameraDir = Helper.previousDir(self.robot.curDir)
        if not Helper.isBoundary(self.robot.curRow + di[cameraDir.value] * 2,
                                 self.robot.curCol + dj[cameraDir.value] * 2):
            self.captureImage()
        elif self.realRun:
            time.sleep(0.1)
        # self.captureImage()
        if sense and action == Action.MOVE_FORWARD:
            self.records[self.robot.curRow][self.robot.curCol][self.robot.curDir.value] += 1
            if self.records[self.robot.curRow][self.robot.curCol][self.robot.curDir.value] >= 2:
                print("Move in the loop:", self.robot.curRow, self.robot.curCol, self.robot.curDir)
                self.moveRobot(Action.TURN_RIGHT, sense, exploredImages=self.exploredImages)
                print("Turn right to exit loop")
                while not self.lookLeft():
                    self.moveRobot(Action.TURN_RIGHT, sense, exploredImages=self.exploredImages)
                    print("Turn right to exit loop")
                print(self.robot.curRow, self.robot.curCol, self.robot.curDir.value)
                for i in range(ROW_SIZE):
                    for j in range(COL_SIZE):
                        print(self.records[i][j], end=" ")
                    print()
                self.records[self.robot.curRow][self.robot.curCol][self.robot.curDir.value] = 0

        if self.realRun:
            # time.sleep(0.1)
            if action == Action.MOVE_FORWARD:
                self.forwardCnt += 1
                if self.forwardCnt == 3:
                    CommManager.sendMsg(CommandType.CALIBRATE)
                    # Helper.waitForCommand(CommandType.ACTION_COMPLETE)
                    Helper.processCmdAndImage(CommandType.ACTION_COMPLETE, exploredImages, self.simulator)
                    self.justCalibrate = True
                    self.forwardCnt = 0
                    time.sleep(0.05)
            else:
                self.forwardCnt = 0

    def captureImage(self):
        self.robot.updateCameraPos()
        self.robot.captureImage(self.exploredImages, self.realImages, self.realMaze)

    def printExploredImages(self):
        print("Done image finding!")
        print("Number of explored images:", len(self.exploredImages))
        print(self.exploredImages)

    def initializeNeedHug(self):
        self.needHug = Helper.init2dArray(ROW_SIZE, COL_SIZE, True)
        visited = Helper.init2dArray(ROW_SIZE, COL_SIZE, False)
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                if 0 <= i <= 2 or ROW_SIZE - 3 <= i <= ROW_SIZE - 1 or 0 <= j <= 2 or COL_SIZE - 3 <= j <= COL_SIZE - 1:
                    if self.exploredMaze[i][j].isExplored and self.exploredMaze[i][j].isObstacle:
                        self.dfs(i, j, visited)
                if self.exploredMaze[i][j].isExplored and not self.exploredMaze[i][j].isObstacle:
                    self.needHug[i][j] = False

    def dfs(self, ui, uj, visited):
        visited[ui][uj] = True
        self.needHug[ui][uj] = False
        for t in range(4):
            vi = ui + di[t]
            vj = uj + dj[t]
            if Helper.isValidCoordinates(vi, vj) and not visited[vi][vj] and self.exploredMaze[vi][vj].isObstacle:
                self.dfs(vi, vj, visited)

    # Can recognize 3 cells at a time
    def updateNeedHug(self):
        cellDir = Helper.previousDir(self.robot.curDir)
        r = self.robot.curRow + di[cellDir.value] * 2
        c = self.robot.curCol + dj[cellDir.value] * 2
        for dt in range(-1, 2):
            if di[cellDir.value] == 0:
                if Helper.isValidCoordinates(r + dt, c):
                    self.needHug[r + dt][c] = False
            elif dj[cellDir.value] == 0:
                if Helper.isValidCoordinates(r, c + dt):
                    self.needHug[r][c + dt] = False

    def leftCellToHug(self):
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                if self.needHug[i][j]:
                    return True
        return False

    def findFirstCellToHug(self):
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                if self.needHug[i][j] and super().canVisit(i + di[Direction.DOWN.value] * 2,
                                                           j + dj[Direction.DOWN.value] * 2):
                    return i, j, Direction.DOWN
        return None

    def goToCellToHug(self):
        startHugRow = None
        startHugCol = None
        startHugDir = None
        # Check whether current position can start to hug
        for t in range(4):
            r = self.robot.curRow + di[t] * 2
            c = self.robot.curCol + dj[t] * 2
            if Helper.isValidCoordinates(r, c) and self.needHug[r][c]:
                startHugRow = r
                startHugCol = c
                startHugDir = Direction((t + 2) % 4)
                targetDir = Direction((t + 1) % 4)
                while self.robot.curDir != targetDir:
                    targetAction = Helper.getTargetTurn(self.robot.curDir, targetDir)
                    self.moveRobot(targetAction, sense=False)
                self.updateNeedHug()
                break
        if startHugRow is None or startHugCol is None or startHugDir is None:
            firstCellToHug = self.findFirstCellToHug()
            if firstCellToHug is not None:
                startHugRow, startHugCol, startHugDir = firstCellToHug
                actions = FastestPath(self.exploredMaze, self.robot, startHugRow + di[startHugDir.value] * 2,
                                      startHugCol + dj[startHugDir.value] * 2, self.realRun).runFastestPath(execute=False)
                self.executeFastestPath(actions)
                targetDir = Helper.previousDir(startHugDir)
                captured = False
                while self.robot.curDir != targetDir:
                    targetAction = Helper.getTargetTurn(self.robot.curDir, targetDir)
                    self.moveRobot(targetAction, sense=False)
                    captured = True
                if not captured:
                    self.captureImage()
                self.updateNeedHug()
        return startHugRow, startHugCol, startHugDir

    def getStopHugCell(self, startHugRow, startHugCol, startHugDir):
        cellToTheLeftRow = startHugRow + di[Helper.nextDir(startHugDir).value]
        cellToTheLeftCol = startHugCol + dj[Helper.nextDir(startHugDir).value]
        if self.needHug[cellToTheLeftRow][cellToTheLeftCol]:
            stopHugRow = cellToTheLeftRow
            stopHugCol = cellToTheLeftCol
            stopHugDir = startHugDir
        else:
            stopHugRow = startHugRow
            stopHugCol = startHugCol
            stopHugDir = Helper.nextDir(startHugDir)
        return stopHugRow, stopHugCol, stopHugDir

    def executeFastestPath(self, actions):
        # print("executeFastestPath")
        if not self.realRun:
            for action in actions:
                self.robot.move(action, sendMsg=False)
            return

        fCount = 0
        for i in range(len(actions)):
            if time.time() >= self.endTime:
                break
            action = actions[i]
            if action == Action.MOVE_FORWARD:
                fCount += 1
                if fCount == 2:
                    obstacleAvoid = False
                    self.robot.moveForwardMultiple(fCount, obstacleAvoid)
                    Helper.waitForCommand(CommandType.ACTION_COMPLETE)
                    time.sleep(0.05)
                    fCount = 0
                    CommManager.sendMsg(CommandType.CALIBRATE)
                    Helper.waitForCommand(CommandType.ACTION_COMPLETE)
                    time.sleep(0.05)
            else:
                if fCount > 0:
                    self.robot.moveForwardMultiple(fCount, obstacleAvoid=False)
                    Helper.waitForCommand(CommandType.ACTION_COMPLETE)
                    time.sleep(0.05)
                    fCount = 0
                self.robot.move(action, sendMsg=True)
                Helper.waitForCommand(CommandType.ACTION_COMPLETE)
                time.sleep(0.05)

        if fCount > 0:
            obstacleAvoid = False
            self.robot.moveForwardMultiple(fCount, obstacleAvoid)
            Helper.waitForCommand(CommandType.ACTION_COMPLETE)
            time.sleep(0.05)
