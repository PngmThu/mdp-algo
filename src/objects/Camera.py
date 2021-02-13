from ..static.Constants import di, dj, MAX_DISTANCE, CAMERA_RANGE
from ..static.Direction import Direction
from ..utils.Helper import Helper


class Camera:

    def __init__(self, row, col, direction):
        self.curRow = row
        self.curCol = col
        self.curDir = direction

    def setPos(self, row, col, direction):
        self.curRow = row
        self.curCol = col
        self.curDir = direction

    """
    Return the list of (x, y) of identified images or empty list if no image is detected
    > exploredImages: the set of (row, col, direction) of images that have been explored
    > realImages: the set of (row, col, direction) of real images
    > realMaze: the real maze that should contains images
    """
    def capture(self, exploredImages, realImages, realMaze):
        result = []
        dr = di[self.curDir.value]
        dc = dj[self.curDir.value]

        halfRange = int((CAMERA_RANGE - 1) / 2)
        for offset in range(-halfRange, halfRange + 1):
            for dist in range(2, MAX_DISTANCE):
                row = self.curRow + dist * dr
                col = self.curCol + dist * dc
                if self.curDir == Direction.UP or self.curDir == Direction.DOWN:
                    col += offset
                else:
                    row += offset
                if Helper.isBoundary(row, col) or (Helper.isValidCoordinates(row, col) and realMaze[row][col].isObstacle):
                    image = (row, col, Helper.oppositeDir(self.curDir))
                    if image in realImages and image not in exploredImages:
                        exploredImages.add(image)
                        result.append(image)
                    break
        return result
