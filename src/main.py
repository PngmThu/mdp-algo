from threading import Thread

from src.algorithms.Exploration import Exploration
from src.algorithms.ImageFinding import ImageFinding
from src.communication.CommManager import CommManager
from src.communication.CommandType import CommandType
from src.objects.Robot import Robot
from src.objects.Cell import Cell
from src.static.Color import Color
from src.static.Constants import ROW_SIZE, COL_SIZE, GOAL_ROW, GOAL_COL, START_ROW, START_COL
from src.static.Direction import Direction
from src.utils.Helper import Helper
from src.algorithms.FastestPath import FastestPath
from src.utils.Simulator import Simulator

fastestPathDone = False


def loadArena():
    file1 = open("../arenas/arena4.txt", 'r')
    lines = file1.readlines()

    arena = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
    for i in range(len(lines)):
        for j in range(COL_SIZE):
            arena[i][j] = int(lines[i][j])

    file1.close()
    return arena


def main():
    """ Test CommManager """
    # CommManager.connect()
    #
    # # Need to use mutex to make sure that 2 commands are well-received
    # CommManager.sendMsg("COMMAND_TYPE", ["abc", "xyz"])
    # # time.sleep(1) # sleep 1s
    # CommManager.sendMsg("NO_DATE_COMMAND_TYPE")
    #
    # CommManager.recvMsg()
    # print("First received message")
    #
    # CommManager.recvMsg()
    # print("Second received message")

    printMenu()
    choice = int(input("Enter your choice: "))
    while 1 <= choice <= 6:
        arena = loadArena()
        # Fastest Path
        if choice == 1 or choice == 2:
            scoreMaze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
            maze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
            fastestPathInit(arena, scoreMaze, maze)

            if choice == 1:
                realRun = False
            else:
                realRun = True
            robot = Robot(START_ROW, START_COL, realRun)
            simulator = Simulator(scoreMaze, robot)
            robot.setSimulator(simulator)

            # Real run
            if choice == 2:
                CommManager.connect()
                msg = CommManager.recvMsg()
                while msg != CommandType.FP_START.value:
                    msg = CommManager.recvMsg()
            # Start fastest path in a new thread
            FPthread = Thread(
                target=lambda: FastestPath(maze, robot, GOAL_ROW, GOAL_COL, realRun).runFastestPath(),
                daemon=True)
            FPthread.start()

            simulator.run()
        # Exploration
        elif choice == 3 or choice == 4:
            scoreMaze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
            exploredMaze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
            realMaze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
            explorationInit(scoreMaze, exploredMaze, arena, realMaze)

            if choice == 3:
                realRun = False
            else:
                realRun = True
            robot = Robot(START_ROW, START_COL, realRun)
            simulator = Simulator(scoreMaze, robot)
            robot.setSimulator(simulator)

            if choice == 4:
                CommManager.connect()
                msg = CommManager.recvMsg()
                while msg != CommandType.EX_START.value:
                    msg = CommManager.recvMsg()

            # Start exploration in a new thread
            EXThread = Thread(
                target=lambda: Exploration(exploredMaze, realMaze, robot, simulator, 3600, 300,
                                           realRun).runExploration(),
                daemon=True)
            EXThread.start()

            simulator.run()
        # Image Finding
        elif choice == 5 or choice == 6:
            scoreMaze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
            exploredMaze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
            realMaze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
            explorationInit(scoreMaze, exploredMaze, arena, realMaze)
            realImages = {(2, 7, Direction.LEFT), (4, 12, Direction.DOWN),
                          (10, 10, Direction.RIGHT), (14, 12, Direction.UP),
                          (13, 1, Direction.UP)}

            if choice == 5:
                realRun = False
            else:
                realRun = True

            robot = Robot(START_ROW, START_COL, realRun)
            simulator = Simulator(scoreMaze, robot)
            robot.setSimulator(simulator)

            if choice == 6:
                CommManager.connect()
                msg = CommManager.recvMsg()
                while msg != CommandType.IF_START.value:
                    msg = CommManager.recvMsg()

            # Start image finding in a new thread
            IFThread = Thread(
                target=lambda: ImageFinding(exploredMaze, realMaze, robot,
                                            simulator, 3600, realRun, realImages).runImageFinding(),
                daemon=True)
            IFThread.start()

            simulator.run()

        printMenu()
        choice = int(input("Enter your choice: "))


def printMenu():
    print()
    print("1) Run simulated fastest path")
    print("2) Run real fastest path")
    print("3) Run simulated exploration")
    print("4) Run real exploration")
    print("5) Run simulated image finding")
    print("6) Run real image finding")


def fastestPathInit(arena, scoreMaze, maze):
    for i in range(ROW_SIZE):
        for j in range(COL_SIZE):
            if arena[i][j] == 1:
                scoreMaze[ROW_SIZE - 1 - i][j] = 1
            else:
                scoreMaze[ROW_SIZE - 1 - i][j] = 0

    for i in range(ROW_SIZE):
        for j in range(COL_SIZE):
            if scoreMaze[i][j] == 1:
                maze[i][j] = Cell(i, j, isObstacle=True)
            else:
                maze[i][j] = Cell(i, j, isObstacle=False)


def explorationInit(scoreMaze, exploredMaze, arena, realMaze):
    for i in range(ROW_SIZE):
        for j in range(COL_SIZE):
            scoreMaze[i][j] = Color.UNEXPLORED.value
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            scoreMaze[START_ROW + dr][START_COL + dc] = Color.START_ZONE.value
            scoreMaze[GOAL_ROW + dr][GOAL_COL + dc] = Color.GOAL_ZONE.value

    for i in range(ROW_SIZE):
        for j in range(COL_SIZE):
            exploredMaze[i][j] = Cell(i, j)
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            exploredMaze[START_ROW + dr][START_COL + dc].isExplored = True
            exploredMaze[GOAL_ROW + dr][GOAL_COL + dc].isExplored = True

    for i in range(ROW_SIZE):
        for j in range(COL_SIZE):
            if arena[i][j] == 1:
                realMaze[ROW_SIZE - 1 - i][j] = Cell(i, j, isObstacle=True)
            else:
                realMaze[ROW_SIZE - 1 - i][j] = Cell(i, j, isObstacle=False)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
