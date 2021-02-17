import enum

from src.static.Action import Action


class CommandType(enum.Enum):

    """ Send """
    ROBOT_POS = "ROBOT_POS"
    MAP = "MAP"
    WAYPOINT = "WAYPOINT"
    FINISH_FASTEST_PATH = "FINISH_FP"
    FINISH_EXPLORATION = "FINISH_EX"
    MOVE_FORWARD = Action.MOVE_FORWARD
    TURN_RIGHT = Action.TURN_RIGHT
    TURN_LEFT = Action.TURN_LEFT
    CALIBRATE = Action.CALIBRATE
    MOVE_FORWARD_MULTIPLE = "FM"
    CAPTURE = "CAPTURE"

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
