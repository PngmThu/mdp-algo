from ..communication.CommandType import CommandType
from ..objects.Robot import Robot
from ..static.Action import Action
from ..static.CalibrationStatus import CalibrationStatus
from ..utils.Helper import Helper
from ..static.Constants import ROW_SIZE, \
    COL_SIZE, INF_COST, di, dj, MAX_FORWARD


class FastestPath:

    # Cell[][] maze, Robot robot
    def __init__(self, maze, robot, destRow, destCol, realRun):
        self.maze = maze
        self.robot = robot
        self.curDir = robot.curDir
        self.candidateCells = set()
        self.visited = Helper.init2dArray(ROW_SIZE, COL_SIZE, False)
        self.parentDict = dict()
        self.curCell = maze[robot.curRow][robot.curCol]
        self.gCosts = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
        self.destRow = destRow
        self.destCol = destCol
        self.realRun = realRun

        # Initialize gCosts 2d array
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                cell = self.maze[i][j]
                if cell.isObstacle:
                    self.gCosts[i][j] = INF_COST
                else:
                    self.gCosts[i][j] = 0

    def getMinCostCell(self):
        minCost = INF_COST
        cellResult = None
        for cell in self.candidateCells:
            gCost = self.gCosts[cell.row][cell.col]
            hCost = Helper.computeCostH(cell, self.destRow, self.destCol)
            cost = gCost + hCost
            if cost < minCost:
                minCost = cost
                cellResult = cell

        return cellResult

    def runFastestPath(self, execute=True):
        print("Calculating fastest path from (" + str(self.curCell.row) + ", "
              + str(self.curCell.col) + ") to goal (" + str(self.destRow) + ", " + str(self.destCol) + ")...")

        self.candidateCells.add(self.curCell)
        self.gCosts[self.curCell.row][self.curCell.col] = 0
        while len(self.candidateCells) != 0:
            self.curCell = self.getMinCostCell()

            # Point the robot in the direction of current from the previous cell
            if self.curCell in self.parentDict:
                self.curDir = Helper.getTargetDir(self.parentDict[self.curCell],
                                                  self.curDir, self.curCell)

            self.visited[self.curCell.row][self.curCell.col] = True
            self.candidateCells.remove(self.curCell)

            if self.curCell.row == self.destRow and self.curCell.col == self.destCol:
                print("Reached destination!")
                pathStack = self.getPath()
                # print fastest path
                Helper.printPath(pathStack)
                # execute path
                actions = self.getActions(pathStack)
                # Calibration
                actionsWithCalibrate = self.getActionsWithCalibrate(actions)
                if execute:
                    self.executePath(actionsWithCalibrate)
                return actionsWithCalibrate

            for t in range(4):
                row = self.curCell.row + di[t]
                col = self.curCell.col + dj[t]
                if self.canVisit(row, col) and not self.visited[row][col]:
                    nextCell = self.maze[row][col]
                    if nextCell not in self.candidateCells:
                        self.parentDict[nextCell] = self.curCell
                        self.gCosts[row][col] = self.gCosts[self.curCell.row][self.curCell.col] + Helper.computeCostG(
                            self.curCell, nextCell, self.curDir)
                        self.candidateCells.add(nextCell)
                    else:
                        currentGCost = self.gCosts[row][col]
                        newGCost = self.gCosts[self.curCell.row][self.curCell.col] + Helper.computeCostG(self.curCell,
                                                                                                         nextCell,
                                                                                                         self.curDir)
                        if newGCost < currentGCost:
                            self.gCosts[row][col] = newGCost
                            self.parentDict[nextCell] = self.curCell

        print("Path not found!")

    def canVisit(self, row, col):
        if 0 < row < ROW_SIZE - 1 and 0 < col < COL_SIZE - 1:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    if not self.maze[row + dr][col + dc].isExplored or self.maze[row + dr][col + dc].isObstacle:
                        return False
            return True
        else:
            return False

    def getPath(self):
        pathStack = [self.maze[self.destRow][self.destCol]]
        while pathStack[-1] in self.parentDict:
            pathStack.append(self.parentDict[pathStack[-1]])
        return pathStack

    def getActions(self, pathStack):
        cur = pathStack[-1]
        direction = self.robot.curDir
        pathStack.pop()
        actions = []
        while len(pathStack) != 0:
            nextCell = pathStack[-1]
            pathStack.pop()
            targetDir = Helper.getTargetDir(cur, direction, nextCell)
            while direction != targetDir:
                targetAction = Helper.getTargetTurn(direction, targetDir)
                direction = Helper.getDirectionAfterTurn(direction, targetAction)
                targetDir = Helper.getTargetDir(cur, direction, nextCell)
                actions.append(targetAction)
            actions.append(Action.MOVE_FORWARD)
            cur = nextCell
        return actions

    def executePath(self, actions):
        if not self.realRun:
            for action in actions:
                self.robot.move(action, sendMsg=False)
            return

        fCount = 0
        for action in actions:
            if action == Action.MOVE_FORWARD:
                fCount += 1
                if fCount == MAX_FORWARD:
                    self.robot.moveForwardMultiple(fCount)
                    Helper.waitForCommand(CommandType.ACTION_COMPLETE)
                    fCount = 0
            else:
                if fCount > 0:
                    self.robot.moveForwardMultiple(fCount)
                    Helper.waitForCommand(CommandType.ACTION_COMPLETE)
                    fCount = 0
                self.robot.move(action, sendMsg=True)
                Helper.waitForCommand(CommandType.ACTION_COMPLETE)

        if fCount > 0:
            self.robot.moveForwardMultiple(fCount)
            Helper.waitForCommand(CommandType.ACTION_COMPLETE)

    # Check whether exist 2 obstacles at the direction
    def canCalibrateAt(self, row, col, direction):
        dr = di[direction.value]
        dc = dj[direction.value]
        if dr != 0:
            cnt = 0
            for j in range(-1, 2):
                if Helper.isBoundary(row + 2 * dr, col + j) or (
                        Helper.isValidCoordinates(row + 2 * dr, col + j) and self.maze[row + 2 * dr][col + j].isExplored and
                        self.maze[row + 2 * dr][col + j].isObstacle):
                    cnt += 1
            # print("cnt:", cnt)
            if cnt >= 2:
                return True
        elif dc != 0:
            cnt = 0
            for i in range(-1, 2):
                if Helper.isBoundary(row + i, col + 2 * dc) or (
                        Helper.isValidCoordinates(row + i, col + 2 * dc) and self.maze[row + i][col + 2 * dc].isExplored and
                        self.maze[row + i][col + 2 * dc].isObstacle):
                    cnt += 1
            # print("cnt:", cnt)
            if cnt >= 2:
                return True
        return False

    def getCalibrationStatus(self, actions):
        tempRobot = Robot(self.robot.curRow, self.robot.curCol, realRun=False)
        tempRobot.setRobotDir(self.robot.curDir)
        statusArr = []
        for action in actions:
            # print(tempRobot.curRow, tempRobot.curCol, tempRobot.curDir)
            if action == Action.TURN_RIGHT or action == Action.TURN_LEFT:
                if self.canCalibrateAt(tempRobot.curRow, tempRobot.curCol, tempRobot.curDir):
                    statusArr.append(CalibrationStatus.AUTO_CALIBRATE)
                else:
                    statusArr.append(CalibrationStatus.CANNOT_CALIBRATE)
                tempRobot.move(action, sendMsg=False, printAction=False)
            else:
                tempRobot.move(action, sendMsg=False, printAction=False)
                # print(tempRobot.curRow, tempRobot.curCol, tempRobot.curDir)
                # If can do front calibrate or left calibrate
                if self.canCalibrateAt(tempRobot.curRow, tempRobot.curCol, tempRobot.curDir) or self.canCalibrateAt(
                        tempRobot.curRow, tempRobot.curCol, Helper.previousDir(tempRobot.curDir)):
                    statusArr.append(CalibrationStatus.FULL_CALIBRATE)
                elif self.canCalibrateAt(tempRobot.curRow, tempRobot.curCol,
                                         Helper.nextDir(tempRobot.curDir)):  # If can do right calibrate
                    statusArr.append(CalibrationStatus.RIGHT_CALIBRATE)
                else:
                    statusArr.append(CalibrationStatus.CANNOT_CALIBRATE)
        # print("Initial statusArr:", statusArr)

        # Process to remove unnecessary calibration
        first = -1
        second = -1
        window = 3
        i = 0
        while i < len(statusArr):
            # print("i:", i)
            for j in range(window):
                if i + j < len(statusArr) and statusArr[i + j] != CalibrationStatus.CANNOT_CALIBRATE:
                    second = i + j
                    if i + j - first > window:  # If the last window have no calibration -> take the first one
                        break
            # print("first", first, "second", second)
            for t in range(i, second):
                statusArr[t] = CalibrationStatus.CANNOT_CALIBRATE
            if second != first:  # If found a calibration
                i = second + 1
            else:
                i += window
            first = second
        # print("Processed statusArr:", statusArr)
        return statusArr

    def getActionsWithCalibrate(self, actions):
        actionsWithCalibrate = []
        statusArr = self.getCalibrationStatus(actions)
        for i in range(len(actions)):
            actionsWithCalibrate.append(actions[i])
            if statusArr[i] == CalibrationStatus.FULL_CALIBRATE:
                actionsWithCalibrate.append(Action.CALIBRATE)
            elif statusArr[i] == CalibrationStatus.RIGHT_CALIBRATE:
                actionsWithCalibrate.append(Action.RIGHT_CALIBRATE)
        return actionsWithCalibrate
