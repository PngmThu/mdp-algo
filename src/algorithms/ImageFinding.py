import time

from .ExplorationAlgo import ExplorationAlgo
from ..communication.CommManager import CommManager
from ..communication.CommandType import CommandType
from ..static.Action import Action
from ..static.Constants import MAX_NUMBER_OF_IMAGES, START_ROW, START_COL, MAX_FORWARD

# Inherit from ExplorationAlgo
from ..utils.Helper import Helper


class ImageFinding(ExplorationAlgo):

    # realImages: the set of (row, col, direction) of real images
    def __init__(self, exploredMaze, realMaze, robot, simulator, timeLimit, realRun, realImages):
        super().__init__(exploredMaze, realMaze, robot, simulator, timeLimit, realRun)
        self.exploredImages = set()
        self.realImages = realImages
        self.forwardCnt = 0

    def runImageFinding(self):
        print("Start image finding...")

        # in seconds
        self.startTime = time.time()
        self.endTime = self.startTime + self.timeLimit

        self.senseAndRepaint()
        self.captureImage()

        self.nextMove()
        while len(self.exploredImages) < MAX_NUMBER_OF_IMAGES and time.time() < self.endTime:
            if self.robot.curRow == START_ROW and self.robot.curCol == START_COL:
                break

            self.nextMove()

        print("Done image finding!")
        print("Number of explored images:", len(self.exploredImages))
        print(self.exploredImages)

        # TO DO: Continue finding images when there are missing images although robot has returned to start zone

    """
        Determines the next move for the robot and executes it accordingly.
        For left hugging, look left first to always have obstacle at the right side
        """

    def nextMove(self):
        if self.lookLeft():
            self.moveRobot(Action.TURN_LEFT)
            if self.lookForward():
                self.moveRobot(Action.MOVE_FORWARD)
        elif self.lookForward():
            self.moveRobot(Action.MOVE_FORWARD)
        elif self.lookRight():
            self.moveRobot(Action.TURN_RIGHT)
            if self.lookForward():
                self.moveRobot(Action.MOVE_FORWARD)
        else:
            self.moveRobot(Action.TURN_RIGHT)
            self.moveRobot(Action.TURN_RIGHT)

    def moveRobot(self, action, exploredImages=None):
        super().moveRobot(action, exploredImages=self.exploredImages)
        self.captureImage()
        if self.realRun:
            if action == Action.MOVE_FORWARD:
                self.forwardCnt += 1
                if self.forwardCnt == MAX_FORWARD:
                    CommManager.sendMsg(CommandType.CALIBRATE)
                    Helper.waitForCommand(CommandType.ACTION_COMPLETE)
                    self.forwardCnt = 0
            else:
                self.forwardCnt = 0

    def captureImage(self):
        self.robot.updateCameraPos()
        self.robot.captureImage(self.exploredImages, self.realImages, self.realMaze)

    def printExploredImages(self):
        print("Done image finding!")
        print("Number of explored images:", len(self.exploredImages))
        print(self.exploredImages)
