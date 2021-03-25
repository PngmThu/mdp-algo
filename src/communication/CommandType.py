import enum


class CommandType(enum.Enum):

    """
    Send:
        P – Algo PC
        I – Image Recognition
        R – Arduino
        A – Android
    """
    # To android
    ROBOT_POS = "A|ROBOT_POS"
    MAP = "A|MAP"
    WAYPOINT = "A|WAYPOINT"
    FINISH = "A|FINISH"
    # To arduino
    MOVE_FORWARD = "R|F"
    MOVE_FORWARD_OBSTACLE_AVOID = "R|FOA"
    TURN_RIGHT = "R|R"
    TURN_LEFT = "R|L"
    TURN_RIGHT_NO_CALIBRATE = "R|RNC"
    TURN_LEFT_NO_CALIBRATE = "R|LNC"
    CALIBRATE = "R|C"
    RIGHT_CALIBRATE = "R|RC"
    FP_START_TO_ARDUINO = "R|FP_START"
    EX_START_TO_ARDUINO = "R|EX_START"
    # To image recognition
    CAPTURE = "I|CAPTURE"

    """ Receive """
    # From image recognition
    IMAGE = "IMAGE"
    DELETE_IMAGE = "DELETE_IMAGE"
    FINISH_IR = "FINISH_IR"
    DONE_CAPTURE = "DONE_CAPTURE"

    # From arduino
    SENSOR_DATA = "SENSOR_DATA"
    ACTION_COMPLETE = "ACTION_COMPLETE"

    # From android
    FP_START = "FP_START"
    EX_START = "EX_START"
    IF_START = "IF_START"
    SET_WAYPOINT = "SET_WAYPOINT"
    RM_WAYPOINT = "RM_WAYPOINT"

