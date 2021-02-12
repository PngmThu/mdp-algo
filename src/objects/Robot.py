from .Camera import Camera
from ..static.Direction import Direction
from ..static.Action import Action
from ..objects.Sensor import Sensor
from ..static.Constants import di, dj, SR_SENSOR_LOWER, SR_SENSOR_UPPER, \
    LR_SENSOR_LOWER, LR_SENSOR_UPPER, offsetRow, offsetCol, GOAL_ROW, GOAL_COL, START_DIR
from ..static.RelativePos import RelativePos
from ..utils.Helper import Helper

"""
 * The robot is represented by a 3 x 3 cell space as below:
 *
 *          ^   ^   ^
 *         SR  SR  SR
 *       < SR
 *        [X] [X] [X] SR >
 *   < LR [X] [X] [X] 
 *        [X] [X] [X]
 *
 * SR = Short Range Sensor, LR = Long Range Sensor
"""


class Robot:

    def __init__(self, row, col):
        self.curRow = row
        self.curCol = col
        self.curDir = START_DIR
        self.touchedGoal = False

        self.SRFrontLeft = Sensor(SR_SENSOR_LOWER, SR_SENSOR_UPPER, "SRFL")
        self.SRFrontCenter = Sensor(SR_SENSOR_LOWER, SR_SENSOR_UPPER, "SRFC")
        self.SRFrontRight = Sensor(SR_SENSOR_LOWER, SR_SENSOR_UPPER, "SRFR")
        self.SRRight = Sensor(SR_SENSOR_LOWER, SR_SENSOR_UPPER, "SRR")
        self.SRLeft = Sensor(SR_SENSOR_LOWER, SR_SENSOR_UPPER, "SRL")
        self.LRLeft = Sensor(LR_SENSOR_LOWER, LR_SENSOR_UPPER, "LRL")

        self.updateSensorsPos()

        # Camera is placed to capture left side of the robot
        self.camera = Camera(row, col, Helper.previousDir(START_DIR))

    def setRobotPos(self, row, col):
        self.curRow = row
        self.curCol = col

    def move(self, action):
        if action == Action.MOVE_FORWARD:
            self.curRow += di[self.curDir.value]
            self.curCol += dj[self.curDir.value]
        elif action == Action.MOVE_BACKWARD:
            self.curRow -= di[self.curDir.value]
            self.curCol -= dj[self.curDir.value]
        elif action == Action.TURN_RIGHT:
            self.curDir = Direction((self.curDir.value + 1) % 4)
        elif action == Action.TURN_LEFT:
            self.curDir = Direction((self.curDir.value + 4 - 1) % 4)

        self.updateTouchedGoal()

        print(action.name)

    # If robot is at goal, update touchedGoal to True
    def updateTouchedGoal(self):
        if self.curRow == GOAL_ROW and self.curCol == GOAL_COL:
            self.touchedGoal = True

    def updateSensorsPos(self):
        self.SRFrontLeft.setPos(self.curRow + offsetRow[(RelativePos.TOP_LEFT.value + self.curDir.value * 2) % 8],
                                self.curCol + offsetCol[(RelativePos.TOP_LEFT.value + self.curDir.value * 2) % 8],
                                self.curDir)
        self.SRFrontCenter.setPos(self.curRow + offsetRow[(RelativePos.TOP.value + self.curDir.value * 2) % 8],
                                  self.curCol + offsetCol[(RelativePos.TOP.value + self.curDir.value * 2) % 8],
                                  self.curDir)
        self.SRFrontRight.setPos(self.curRow + offsetRow[(RelativePos.TOP_RIGHT.value + self.curDir.value * 2) % 8],
                                 self.curCol + offsetCol[(RelativePos.TOP_RIGHT.value + self.curDir.value * 2) % 8],
                                 self.curDir)
        self.SRRight.setPos(self.curRow + offsetRow[(RelativePos.TOP_RIGHT.value + self.curDir.value * 2) % 8],
                            self.curCol + offsetCol[(RelativePos.TOP_RIGHT.value + self.curDir.value * 2) % 8],
                            Helper.nextDir(self.curDir))
        self.SRLeft.setPos(self.curRow + offsetRow[(RelativePos.TOP_LEFT.value + self.curDir.value * 2) % 8],
                           self.curCol + offsetCol[(RelativePos.TOP_LEFT.value + self.curDir.value * 2) % 8],
                           Helper.previousDir(self.curDir))
        self.LRLeft.setPos(self.curRow + offsetRow[(RelativePos.LEFT.value + self.curDir.value * 2) % 8],
                           self.curCol + offsetCol[(RelativePos.LEFT.value + self.curDir.value * 2) % 8],
                           Helper.previousDir(self.curDir))

    """
    Calls the .sense() method of all the attached sensors and stores the received values in an integer array.
    @return [SRFrontLeft, SRFrontCenter, SRFrontRight, SRRight, SRLeft, LRLeft]
    """
    def sense(self, exploredMaze, realMaze):
        result = [self.SRFrontLeft.sense(exploredMaze, realMaze), self.SRFrontCenter.sense(exploredMaze, realMaze),
                  self.SRFrontRight.sense(exploredMaze, realMaze), self.SRRight.sense(exploredMaze, realMaze),
                  self.SRLeft.sense(exploredMaze, realMaze), self.LRLeft.sense(exploredMaze, realMaze)]
        return result

    def updateCameraPos(self):
        self.camera.setPos(self.curRow, self.curCol, Helper.previousDir(self.curDir))

    def captureImage(self, exploredImages, realImages, realMaze):
        return self.camera.capture(exploredImages, realImages, realMaze)
