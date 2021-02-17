from ..static.Action import Action
from ..utils.Helper import Helper
from ..static.Constants import ROW_SIZE, \
    COL_SIZE, INF_COST, di, dj, MAX_FOWARD


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

    def runFastestPath(self):
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
                self.executePath(actions)
                return actions

            for t in range(4):
                row = self.curCell.row + di[t]
                col = self.curCell.col + dj[t]
                if self.canVisit(row, col) and not self.visited[row][col]:
                    nextCell = self.maze[row][col]
                    if nextCell not in self.candidateCells:
                        self.parentDict[nextCell] = self.curCell
                        self.gCosts[row][col] = self.gCosts[self.curCell.row][self.curCell.col] + Helper.computeCostG(self.curCell, nextCell, self.curDir)
                        self.candidateCells.add(nextCell)
                    else:
                        currentGCost = self.gCosts[row][col]
                        newGCost = self.gCosts[self.curCell.row][self.curCell.col] + Helper.computeCostG(self.curCell, nextCell, self.curDir)
                        if newGCost < currentGCost:
                            self.gCosts[row][col] = newGCost
                            self.parentDict[nextCell] = self.curCell

        print("Path not found!")

    def canVisit(self, row, col):
        if 0 < row < ROW_SIZE - 1 and 0 < col < COL_SIZE - 1:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    if self.maze[row + dr][col + dc].isObstacle:
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
                if fCount == MAX_FOWARD:
                    self.robot.moveForwardMultiple(fCount)
                    Helper.receiveActionComplete()
                    fCount = 0
            elif action == Action.TURN_RIGHT or action == Action.TURN_LEFT:
                if fCount > 0:
                    self.robot.moveForwardMultiple(fCount)
                    Helper.receiveActionComplete()
                    fCount = 0
                self.robot.move(action, sendMsg=True)
                Helper.receiveActionComplete()

        if fCount > 0:
            self.robot.moveForwardMultiple(fCount)
            Helper.receiveActionComplete()

    # TO DO: find cell that can stop to calibrate
    def canCalibrateAt(self, row, col, direction):
        # 3 front sensors
        dr = di[direction.value]
        dc = dj[direction.value]
        if dr != 0:
            for j in range(-1, 2):
                if not Helper.isValidCoordinates(self.maze[row + dr][col + j]) or self.maze[row + dr][col + j].isObstacle:
                    return True
        elif dc != 0:
            for i in range(-1, 2):
                if not Helper.isValidCoordinates(self.maze[row + i][col + dc]) or self.maze[row + i][col + dc].isObstacle:
                    return True
