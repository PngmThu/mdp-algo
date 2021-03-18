import time

from .Camera import Camera
from ..communication.CommManager import CommManager
from ..communication.CommandType import CommandType
from ..static.Direction import Direction
from ..static.Action import Action
from ..objects.Sensor import Sensor
from ..static.Constants import di, dj, SR_SENSOR_LOWER, SR_SENSOR_UPPER, \
    LR_SENSOR_LOWER, LR_SENSOR_UPPER, offsetRow, offsetCol, GOAL_ROW, GOAL_COL, START_DIR, SPLITTER, SPEED
from ..static.RelativePos import RelativePos
from ..utils.Helper import Helper
from ..utils.MapDescriptor import MapDescriptor

"""
 * The robot is represented by a 3 x 3 cell space as below:
 *
 *          ^   ^   ^
 *         SR  SR  SR
 *   < SR [X] [X] [X] LR >
 *        [X] [X] [X] 
 *   < SR [X] [X] [X] 
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
        self.speed = SPEED

        self.SRFrontLeft = Sensor(SR_SENSOR_LOWER, SR_SENSOR_UPPER, "SRFL")
        self.SRFrontCenter = Sensor(SR_SENSOR_LOWER, SR_SENSOR_UPPER, "SRFC")
        self.SRFrontRight = Sensor(SR_SENSOR_LOWER, SR_SENSOR_UPPER, "SRFR")
        self.SRLeftHead = Sensor(SR_SENSOR_LOWER, SR_SENSOR_UPPER, "SRLH")
        self.SRLeftTail = Sensor(SR_SENSOR_LOWER, SR_SENSOR_UPPER, "SRLT")
        self.LRRight = Sensor(LR_SENSOR_LOWER, LR_SENSOR_UPPER, "LRR")

        self.updateSensorsPos()

        # Camera is placed to capture left side of the robot
        self.camera = Camera(row, col, Helper.previousDir(START_DIR))

    def setRobotPos(self, row, col):
        self.curRow = row
        self.curCol = col

    def setRobotDir(self, direction):
        self.curDir = direction

    def setSimulator(self, simulator):
        self.simulator = simulator

    def setSpeed(self, speed):
        self.speed = speed

    def move(self, action, sendMsg, printAction=True):
        self.updateSimulator(action)

        if action == Action.MOVE_FORWARD:
            self.curRow += di[self.curDir.value]
            self.curCol += dj[self.curDir.value]
        elif action == Action.MOVE_BACKWARD:
            self.curRow -= di[self.curDir.value]
            self.curCol -= dj[self.curDir.value]
        elif action == Action.TURN_RIGHT or action == Action.TURN_RIGHT_NO_CALIBRATE:
            self.curDir = Direction((self.curDir.value + 1) % 4)
        elif action == Action.TURN_LEFT or action == Action.TURN_LEFT_NO_CALIBRATE:
            self.curDir = Direction((self.curDir.value + 4 - 1) % 4)

        self.updateTouchedGoal()

        if printAction:
            print(action.name)

        if self.realRun:
            # Send action to arduino
            if sendMsg:
                Helper.sendAction(action)
            # Send robot pos to android
            data = [self.curRow, self.curCol, self.curDir.value]
            CommManager.sendMsg(CommandType.ROBOT_POS, data)

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
        self.SRLeftHead.setPos(self.curRow + offsetRow[(RelativePos.TOP_LEFT.value + self.curDir.value * 2) % 8],
                               self.curCol + offsetCol[(RelativePos.TOP_LEFT.value + self.curDir.value * 2) % 8],
                               Helper.previousDir(self.curDir))
        self.SRLeftTail.setPos(self.curRow + offsetRow[(RelativePos.BOTTOM_LEFT.value + self.curDir.value * 2) % 8],
                               self.curCol + offsetCol[(RelativePos.BOTTOM_LEFT.value + self.curDir.value * 2) % 8],
                               Helper.previousDir(self.curDir))
        self.LRRight.setPos(self.curRow + offsetRow[(RelativePos.TOP_RIGHT.value + self.curDir.value * 2) % 8],
                            self.curCol + offsetCol[(RelativePos.TOP_RIGHT.value + self.curDir.value * 2) % 8],
                            Helper.nextDir(self.curDir))

    """
    Calls the .sense() method of all the attached sensors and stores the received values in an integer array.
    @return [SRFrontLeft, SRFrontCenter, SRFrontRight, SRRight, SRLeft, LRLeft]
    """
    def sense(self, exploredMaze, realMaze, exploredImages=None, flipRecord=None):
        if not self.realRun:
            result = [self.SRFrontLeft.sense(exploredMaze, realMaze), self.SRFrontCenter.sense(exploredMaze, realMaze),
                      self.SRFrontRight.sense(exploredMaze, realMaze), self.SRLeftHead.sense(exploredMaze, realMaze),
                      self.SRLeftTail.sense(exploredMaze, realMaze), self.LRRight.sense(exploredMaze, realMaze)]
            # print("P1:", MapDescriptor.generateP1(exploredMaze))
            # print("P2: ", MapDescriptor.generateP2(exploredMaze))
            return result

        # Receive sensor data from arduino
        msgArr = CommManager.recvMsg()
        msgData = []
        while True:
            sensed = False
            for msg in msgArr:
                if msg.startswith(CommandType.SENSOR_DATA.value):
                    msgData = msg.split(SPLITTER)
                    sensed = True
                elif exploredImages is not None:
                    Helper.processMsgForImage(msg, exploredImages, self.simulator)
            if sensed:
                break
            msgArr = CommManager.recvMsg()  # Continue wait for sensor data

        result = []
        for i in range(1, 7):
            result.append(int(msgData[i]))
        if msgData[0] == CommandType.SENSOR_DATA.value:
            self.SRFrontLeft.processSensorVal(exploredMaze, result[0], self.simulator, flipRecord)
            self.SRFrontCenter.processSensorVal(exploredMaze, result[1], self.simulator, flipRecord)
            self.SRFrontRight.processSensorVal(exploredMaze, result[2], self.simulator, flipRecord)
            self.SRLeftHead.processSensorVal(exploredMaze, result[3], self.simulator, flipRecord)
            self.SRLeftTail.processSensorVal(exploredMaze, result[4], self.simulator, flipRecord)
            self.LRRight.processSensorVal(exploredMaze, result[5], self.simulator, flipRecord)

            # Send map descriptor to android
            data = [MapDescriptor.generateP1(exploredMaze), MapDescriptor.generateP2(exploredMaze)]
            CommManager.sendMsg(CommandType.MAP, data)
        return result

    def updateCameraPos(self):
        self.camera.setPos(self.curRow, self.curCol, Helper.previousDir(self.curDir))

    def captureImage(self, exploredImages, realImages, realMaze):
        if not self.realRun:
            images = self.camera.capture(exploredImages, realImages, realMaze)
            if self.simulator is not None:
                # Draw image sticker in simulator
                for image in images:
                    self.simulator.drawImageSticker(image[0], image[1], image[2], image[3])
            return
        # Send camera position and ask to capture image
        data = [self.camera.curRow, self.camera.curCol, self.camera.curDir.value]
        CommManager.sendMsg(CommandType.CAPTURE, data)
        # Helper.waitForCommand(CommandType.DONE_CAPTURE)  # Wait for done capturing
        Helper.processCmdAndImage(CommandType.DONE_CAPTURE, exploredImages, self.simulator)

    def moveForwardMultiple(self, count, obstacleAvoid):
        if count == 1:
            self.move(Action.MOVE_FORWARD, sendMsg=True)
            return
        if not obstacleAvoid:
            CommManager.sendMsg(CommandType.MOVE_FORWARD, count)
        else:
            CommManager.sendMsg(CommandType.MOVE_FORWARD_OBSTACLE_AVOID, count)
        while count != 0:
            self.move(Action.MOVE_FORWARD, sendMsg=False)
            count -= 1

    def updateSimulator(self, action):
        if self.simulator is not None:
            time.sleep(self.speed)  # in seconds
            self.simulator.updateRobotPos(action)
