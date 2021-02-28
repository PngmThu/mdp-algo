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
    FINISH_FASTEST_PATH = "A|FINISH_FP"
    # To android and arduino
    FINISH_EXPLORATION = "RA|FINISH_EX"
    # To arduino
    MOVE_FORWARD = "R|F"
    TURN_RIGHT = "R|R"
    TURN_LEFT = "R|L"
    CALIBRATE = "R|C"
    RIGHT_CALIBRATE = "R|RC"
    # To image recognition
    CAPTURE = "I|CAPTURE"

    """ Receive """
    # From image recognition
    IMAGE = "IMAGE"
    DELETE_IMAGE = "DELETE_IMAGE"
    FINISH_IR = "FINISH_IR"

    # From arduino
    SENSOR_DATA = "SENSOR_DATA"
    ACTION_COMPLETE = "ACTION_COMPLETE"

    # From android
    FP_START = "FP_START"
    EX_START = "EX_START"
    IF_START = "IF_START"
    SET_WAYPOINT = "SET_WAYPOINT"
    RM_WAYPOINT = "RM_WAYPOINT"

