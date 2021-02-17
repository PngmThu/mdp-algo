import time

from .Camera import Camera
from ..communication.CommManager import CommManager
from ..communication.CommandType import CommandType
from ..static.Direction import Direction
from ..static.Action import Action
from ..objects.Sensor import Sensor
from ..static.Constants import di, dj, SR_SENSOR_LOWER, SR_SENSOR_UPPER, \
    LR_SENSOR_LOWER, LR_SENSOR_UPPER, offsetRow, offsetCol, GOAL_ROW, GOAL_COL, START_DIR, SPLITTER
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

    def __init__(self, row, col, realRun):
        self.curRow = row
        self.curCol = col
        self.curDir = START_DIR
        self.touchedGoal = False
        self.realRun = realRun
        self.simulator = None

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

    def setSimulator(self, simulator):
        self.simulator = simulator

    def move(self, action, sendMsg):
        self.updateSimulator(action)

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

        if self.realRun and sendMsg:
            self.sendAction(action)

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
        if not self.realRun:
            result = [self.SRFrontLeft.sense(exploredMaze, realMaze), self.SRFrontCenter.sense(exploredMaze, realMaze),
                      self.SRFrontRight.sense(exploredMaze, realMaze), self.SRRight.sense(exploredMaze, realMaze),
                      self.SRLeft.sense(exploredMaze, realMaze), self.LRLeft.sense(exploredMaze, realMaze)]
            return result

        # Receive sensor data from arduino
        msg = CommManager.recvMsg()
        msgArr = msg.split(SPLITTER)
        while msgArr[0] != CommandType.SENSOR_DATA.value:
            # If an image is identified
            if msgArr[0] == CommandType.IMAGE.value:
                row = int(msgArr[1])
                col = int(msgArr[2])
                direction = int(msgArr[3])
                if self.simulator is not None:
                    self.simulator.drawImageSticker(row, col, Direction(direction))
            msg = CommManager.recvMsg()
            msgArr = msg.split(SPLITTER)

        result = []
        for i in range(1, 7):
            result.append(int(msgArr[i]))
        if msgArr[0] == CommandType.SENSOR_DATA.value:
            self.SRFrontLeft.processSensorVal(exploredMaze, result[0])
            self.SRFrontCenter.processSensorVal(exploredMaze, result[1])
            self.SRFrontRight.processSensorVal(exploredMaze, result[2])
            self.SRRight.processSensorVal(exploredMaze, result[3])
            self.SRLeft.processSensorVal(exploredMaze, result[4])
            self.LRLeft.processSensorVal(exploredMaze, result[5])

            # TO DO: Send map descriptor to android
        return result

    def updateCameraPos(self):
        self.camera.setPos(self.curRow, self.curCol, Helper.previousDir(self.curDir))

    def captureImage(self, exploredImages, realImages, realMaze):
        if not self.realRun:
            images = self.camera.capture(exploredImages, realImages, realMaze)
            if self.simulator is not None:
                # Draw image sticker in simulator
                for image in images:
                    self.simulator.drawImageSticker(image[0], image[1], image[2])
            return
        # Send camera position and ask to capture image
        data = [self.camera.curRow, self.camera.curCol, self.camera.curDir.value]
        CommManager.sendMsg(CommandType.CAPTURE.value, data)

    def sendAction(self, action):
        # Send action to arduino
        # print("Send action!!!")
        CommManager.sendMsg(action.value)
        if action != Action.CALIBRATE:
            # Send robot position to android
            data = [self.curRow, self.curCol, self.curDir.value]
            CommManager.sendMsg(CommandType.ROBOT_POS.value, data)

    def moveForwardMultiple(self, count):
        if count == 1:
            self.move(Action.MOVE_FORWARD, sendMsg=True)
            return
        CommManager.sendMsg(CommandType.MOVE_FORWARD_MULTIPLE.value, count)
        while count != 0:
            self.move(Action.MOVE_FORWARD, sendMsg=False)
            count -= 1

        # Send robot position to android
        dataArr = [self.curRow, self.curCol, self.curDir.value]
        CommManager.sendMsg(CommandType.ROBOT_POS.value, dataArr)

    def updateSimulator(self, action):
        if self.simulator is not None:
            time.sleep(0.1)  # sleep 100ms
            self.simulator.updateRobotPos(action)