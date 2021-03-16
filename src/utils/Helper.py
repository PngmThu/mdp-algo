from ..communication.CommManager import CommManager
from ..communication.CommandType import CommandType
from ..static.Constants import \
    GOAL_ROW, GOAL_COL, MOVE_COST, TURN_COST, ROW_SIZE, COL_SIZE, START_ROW, START_COL, di, dj, SPLITTER
from ..static.Direction import Direction
from ..static.Action import Action


class Helper:

    @staticmethod
    def init2dArray(numrow, numcol, val):
        return [[val for x in range(numcol)] for y in range(numrow)]

    # Compute heuristic cost h(n) from a cell to goal
    # Heuristic: The number of moves has to be made
    @staticmethod
    def computeCostH(cell, destRow, destCol):
        cost = (abs(destRow - cell.row) + abs(destCol - cell.col)) * MOVE_COST
        if (destRow - cell.row) != 0 and (destCol - cell.col) != 0:
            cost += TURN_COST
        return cost

    # Get target direction from current cell to target cell
    @staticmethod
    def getTargetDir(curCell, curDir, targetCell):
        if (curCell.col - targetCell.col) > 0:
            return Direction.LEFT
        elif (targetCell.col - curCell.col) > 0:
            return Direction.RIGHT
        else:
            if (curCell.row - targetCell.row) > 0:
                return Direction.DOWN
            elif (targetCell.row - curCell.row) > 0:
                return Direction.UP
            else:
                return curDir

    # Turn cost from direction 1 to direction 2
    @staticmethod
    def getTurnCost(dir1, dir2):
        numOfTurn = abs(dir2.value - dir1.value)
        if numOfTurn == 3:
            numOfTurn = 1
        return TURN_COST * numOfTurn

    @staticmethod
    def computeCostG(curCell, targetCell, curDir):
        targetDir = Helper.getTargetDir(curCell, curDir, targetCell)
        turnCost = Helper.getTurnCost(curDir, targetDir)
        return MOVE_COST + turnCost

    # Print path from a path stack
    @staticmethod
    def printPath(pathStack):
        pathCopy = pathStack.copy()
        while len(pathCopy) != 0:
            temp = pathCopy.pop()
            print(str(temp.row) + ", " + str(temp.col))

    # Get target action from 1 cell to target cell
    @staticmethod
    def getTargetTurn(curDir, targetDir):
        if targetDir.value == curDir.value:
            return Action.MOVE_FORWARD
        elif (targetDir.value - curDir.value) == 1:
            return Action.TURN_RIGHT
        elif targetDir == Direction.UP and curDir == Direction.LEFT:
            return Action.TURN_RIGHT
        else:
            return Action.TURN_LEFT

    # Get target action from 1 cell to target cell
    @staticmethod
    def getDirectionAfterTurn(direction, action):
        if action == Action.TURN_RIGHT:
            return Direction((direction.value + 1) % 4)
        elif action == Action.TURN_LEFT:
            return Direction((direction.value + 4 - 1) % 4)
        else:
            return direction

    # Check valid coordinates
    @staticmethod
    def isValidCoordinates(row, col):
        return 0 <= row < ROW_SIZE and 0 <= col < COL_SIZE

    @staticmethod
    def inStartZone(row, col):
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if row == START_ROW + dr and col == START_COL + dc:
                    return True
        return False

    @staticmethod
    def inGoalZone(row, col):
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if row == GOAL_ROW + dr and col == GOAL_COL + dc:
                    return True
        return False

    @staticmethod
    def nextDir(direction):
        return Direction((direction.value + 1) % 4)

    @staticmethod
    def previousDir(direction):
        return Direction((direction.value + 4 - 1) % 4)

    @staticmethod
    def oppositeDir(direction):
        return Direction((direction.value + 2) % 4)

    @staticmethod
    def neighborOfUnexploredCellAt(row, col, direction):
        r = row + di[direction.value] * 2
        c = col + dj[direction.value] * 2
        return r, c

    @staticmethod
    def isBoundary(row, col):
        if (row == -1 or row == ROW_SIZE) and 0 <= col < COL_SIZE:
            return True
        if (col == -1 or col == COL_SIZE) and 0 <= row < ROW_SIZE:
            return True
        return False

    @staticmethod
    def processMsgForImage(msg, exploredImages, simulator):
        if msg.startswith(CommandType.IMAGE.value):
            data = msg.split(SPLITTER)
            imageId = int(data[1])
            row = int(data[2])
            col = int(data[3])
            direction = Direction(int(data[4]))
            if Helper.isBoundary(row, col) or Helper.isValidCoordinates(row, col):
                exploredImages.add(imageId)
                if simulator is not None:
                    # Draw image sticker in simulator
                    simulator.drawImageSticker(imageId, row, col, direction)

    @staticmethod
    def processCmdAndImage(cmdType, exploredImages, simulator):
        msgArr = CommManager.recvMsg()
        while True:
            received = False
            for msg in msgArr:
                if msg.startswith(cmdType.value):
                    received = True
                elif exploredImages is not None:
                    Helper.processMsgForImage(msg, exploredImages, simulator)
            if received:
                break
            msgArr = CommManager.recvMsg()  # Continue wait for action complete

    @staticmethod
    def waitForCommand(commandType):
        msgArr = CommManager.recvMsg()
        while True:
            received = False
            for msg in msgArr:
                if msg.startswith(commandType.value):
                    received = True
                    break
            if received:
                break
            msgArr = CommManager.recvMsg()  # Continue wait for the command

    @staticmethod
    def actionToCmd(action):
        if action == Action.MOVE_FORWARD:
            return CommandType.MOVE_FORWARD
        elif action == Action.TURN_RIGHT:
            return CommandType.TURN_RIGHT
        elif action == Action.TURN_LEFT:
            return CommandType.TURN_LEFT
        elif action == Action.CALIBRATE:
            return CommandType.CALIBRATE
        elif action == Action.RIGHT_CALIBRATE:
            return CommandType.RIGHT_CALIBRATE
        elif action == Action.TURN_RIGHT_NO_CALIBRATE:
            return CommandType.TURN_RIGHT_NO_CALIBRATE
        elif action == Action.TURN_LEFT_NO_CALIBRATE:
            return CommandType.TURN_LEFT_NO_CALIBRATE

    @staticmethod
    def sendAction(action):
        # Send action to arduino
        if action == Action.MOVE_FORWARD:
            data = [1]
            CommManager.sendMsg(Helper.actionToCmd(action), 1)
        else:
            CommManager.sendMsg(Helper.actionToCmd(action))

    @staticmethod
    def getTargetDirForUnexplored(curCell, curDir, targetCell):
        if (curCell.col - targetCell.col) > 1:
            return Direction.LEFT
        elif (targetCell.col - curCell.col) > 1:
            return Direction.RIGHT
        else:
            if (curCell.row - targetCell.row) > 1:
                return Direction.DOWN
            elif (targetCell.row - curCell.row) > 1:
                return Direction.UP
            else:
                return curDir

    @staticmethod
    def isValidWayPoint(maze, waypointRow, waypointCol):
        if waypointRow is None or waypointCol is None:
            return False
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                row = waypointRow + dr
                col = waypointCol + dc
                if not Helper.isValidCoordinates(row, col) or maze[row][col].isObstacle:
                    return False
        return True
