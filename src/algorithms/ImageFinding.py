import time

from .ExplorationAlgo import ExplorationAlgo
from ..static.Constants import MAX_NUMBER_OF_IMAGES


# Inherit from ExplorationAlgo
class ImageFinding(ExplorationAlgo):

    # realImages: the set of (row, col, direction) of real images
    def __init__(self, exploredMaze, realMaze, robot, simulator, timeLimit, realImages):
        super().__init__(exploredMaze, realMaze, robot, simulator, timeLimit)
        self.exploredImages = set()
        self.realImages = realImages

    def runImageFinding(self):
        print("Start image finding...")

        # in seconds
        self.startTime = time.time()
        self.endTime = self.startTime + self.timeLimit

        self.senseAndRepaint()

        self.executeNextMove()
        # self.nextMove()
        # while len(self.exploredImages) < MAX_NUMBER_OF_IMAGES and time.time() < self.endTime:
        #     if self.robot.curRow == START_ROW and self.robot.curCol == START_COL:
        #         break
        #
        #     self.nextMove()
        #
        # print("Done image finding!")
        # print("Number of explored images:", len(self.exploredImages))
        # print(self.exploredImages)

        # TO DO: Continue finding images when there are missing images although robot has returned to start zone

    def executeNextMove(self):
        self.nextMove()

        # if self.robot.curRow == START_ROW and self.robot.curCol == START_COL:
        #     return

        if len(self.exploredImages) < MAX_NUMBER_OF_IMAGES and time.time() < self.endTime:
            self.simulator.window.after(150, lambda: self.executeNextMove())
        else:
            self.printExploredImages()

    def moveRobot(self, action):
        super().moveRobot(action)
        self.captureImage()

    def captureImage(self):
        self.robot.updateCameraPos()
        images = self.robot.captureImage(self.exploredImages, self.realImages, self.realMaze)
        if self.simulator is None:
            return
        # Draw image sticker in simulator
        for image in images:
            self.simulator.drawImageSticker(image[0], image[1], image[2])

    def printExploredImages(self):
        print("Done image finding!")
        print("Number of explored images:", len(self.exploredImages))
        print(self.exploredImages)
