from .Helper import Helper
from ..objects.Cell import Cell
from ..static.Constants import ROW_SIZE, COL_SIZE


class MapDescriptor:

    @staticmethod
    def binToHex(binStr):
        hexStr = hex(int(binStr, 2))
        return hexStr[2:].upper()

    @staticmethod
    def hexToBin(hexStr):
        scale = 16  # equals to hexadecimal
        num_of_bits = 4
        return bin(int(hexStr, scale))[2:].zfill(num_of_bits)

    @staticmethod
    def generateP1(maze):
        # Padding "11" at the beginning
        res = ""
        binStr = "11"
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                if maze[i][j].isExplored:
                    binStr += "1"
                else:
                    binStr += "0"

                if len(binStr) == 4:
                    res += MapDescriptor.binToHex(binStr)
                    binStr = ""
        binStr += "11"  # padding "11" at the end
        res += MapDescriptor.binToHex(binStr)
        return res

    @staticmethod
    def generateP2(maze):
        res = ""
        binStr = ""
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                if maze[i][j].isExplored:
                    if maze[i][j].isObstacle:
                        binStr += "1"
                    else:
                        binStr += "0"

                    if len(binStr) == 4:
                        res += MapDescriptor.binToHex(binStr)
                        binStr = ""
        if len(binStr) > 0:
            length = len(binStr)
            for i in range(4 - length):
                binStr += "0"
            res += MapDescriptor.binToHex(binStr)
        # Make to full bytes
        if len(res) % 2 == 1:
            res += "0"
        return res

    @staticmethod
    def convertToMaze(hexP2):
        binP2 = ""
        for c in hexP2:
            binP2 += MapDescriptor.hexToBin(c)
        maze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
        for i in range(ROW_SIZE):
            for j in range(COL_SIZE):
                ch = binP2[i * COL_SIZE + j]
                if ch == '1':
                    maze[i][j] = Cell(i, j, isObstacle=True)
                else:
                    maze[i][j] = Cell(i, j, isObstacle=False)
                maze[i][j].isExplored = True
        return maze
