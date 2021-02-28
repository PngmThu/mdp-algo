import enum


class CalibrationStatus(enum.Enum):
    CANNOT_CALIBRATE = 0
    FULL_CALIBRATE = 1
    RIGHT_CALIBRATE = 2
    AUTO_CALIBRATE = 3   # Before turn left or turn right, a front calibrate is performed if exists obstacles
