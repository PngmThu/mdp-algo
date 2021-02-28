import time

from .ExplorationAlgo import ExplorationAlgo
from ..static.Constants import MAX_NUMBER_OF_IMAGES, START_ROW, START_COL


# Inherit from ExplorationAlgo
class ImageFinding(ExplorationAlgo):

    # realImages: the set of (row, col, direction) of real images
    def __init__(self, exploredMaze, realMaze, robot, simulator, timeLimit, realRun, realImages):
        super().__init__(exploredMaze, realMaze, robot, simulator, timeLimit, realRun)
        self.exploredImages = set()
        self.realImages = realImages

    def runImageFinding(self):
        print("Start image finding...")

        # in seconds
        self.startTime = time.time()
        self.endTime = self.startTime + self.timeLimit

        self.captureImage()
        self.senseAndRepaint()

        self.nextMove()
        while len(self.exploredImages) < MAX_NUMBER_OF_IMAGES and time.time() < self.endTime:
            if self.robot.curRow == START_ROW and self.robot.curCol == START_COL:
                break

            self.nextMove()

        print("Done image finding!")
        print("Number of explored images:", len(self.exploredImages))
        print(self.exploredImages)

        # TO DO: Continue finding images when there are missing images although robot has returned to start zone

    def moveRobot(self, action, exploredImages=None):
        super().moveRobot(action, exploredImages=self.exploredImages)
        self.captureImage()

    def captureImage(self):
        self.robot.updateCameraPos()
        self.robot.captureImage(self.exploredImages, self.realImages, self.realMaze)

    def printExploredImages(self):
        print("Done image finding!")
        print("Number of explored images:", len(self.exploredImages))
        print(self.exploredImages)
