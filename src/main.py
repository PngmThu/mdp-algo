from threading import Thread

from src.algorithms.Exploration import Exploration
from src.algorithms.ImageFinding import ImageFinding
from src.communication.CommManager import CommManager
from src.communication.CommandType import CommandType
from src.objects.Robot import Robot
from src.objects.Cell import Cell
from src.static.Color import Color
from src.static.Constants import ROW_SIZE, COL_SIZE, GOAL_ROW, GOAL_COL, START_ROW, START_COL, SPEED, SPLITTER
from src.static.Direction import Direction
from src.utils.Helper import Helper
from src.algorithms.FastestPath import FastestPath
from src.utils.MapDescriptor import MapDescriptor
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

    # Need to use mutex to make sure that 2 commands are well-received
    # CommManager.sendMsg("AI|DoSomething1\nAI|DoSomething2\n")
    # CommManager.sendMsg("AI|DoSomething2\n")
    # CommManager.sendMsg("I|DoSomething\n")
    # while True:
    #     msg = input("Enter a msg: ")
    #     CommManager.sendNormalMsg(msg)
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
        loadChoice = input("Load maze from map descriptor P2? (Y/N): ")
        if loadChoice == "Y":
            hexP2 = input("Enter map descriptor P2: ")
            maze = loadMazeFromMapDescriptorP2(hexP2)
        else:
            maze = loadMazeFromArenaFile()

        waypointRow = None
        waypointCol = None
        # waypointRow = 15
        # waypointCol = 2

        # Fastest Path
        if choice == 1 or choice == 2:
            """   Enter way point here"""
            waypointRow = None
            waypointCol = None
            scoreMaze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
            fastestPathInit(maze, scoreMaze)

            if choice == 1:
                realRun = False
                """   Enter way point for simulated run   """
                # waypointRow = 15
                # waypointCol = 2
                if Helper.isValidWayPoint(maze, waypointRow, waypointCol):
                    scoreMaze[waypointRow][waypointCol] = Color.WAYPOINT.value
            else:
                realRun = True

            # Real run
            if choice == 2:
                CommManager.connect()

                # Send map descriptor to android
                data = [MapDescriptor.generateP1(maze), MapDescriptor.generateP2(maze)]
                CommManager.sendMsg(CommandType.MAP, data)

                msgArr = CommManager.recvMsg()
                while True:
                    start = False
                    for msg in msgArr:
                        if msg.startswith(CommandType.FP_START.value):
                            start = True
                            break
                        elif msg.startswith(CommandType.SET_WAYPOINT.value):
                            data = msg.split(SPLITTER)
                            row = int(data[1])
                            col = int(data[2])
                            if Helper.isValidWayPoint(maze, row, col):
                                waypointRow = row
                                waypointCol = col
                                scoreMaze[waypointRow][waypointCol] = Color.WAYPOINT.value
                                # CommManager.sendMsg(CommandType.WAYPOINT, data[1:])
                        elif msg.startswith(CommandType.RM_WAYPOINT.value):
                            if Helper.isValidWayPoint(maze,waypointRow, waypointCol):
                                scoreMaze[waypointRow][waypointCol] = Color.EMPTY_CELL.value
                            waypointRow = None
                            waypointCol = None
                    if start:
                        break
                    msgArr = CommManager.recvMsg()  # Continue wait for FP_START

            robot = Robot(START_ROW, START_COL, realRun)
            simulator = Simulator(scoreMaze, robot)
            robot.setSimulator(simulator)

            FPthread = Thread(
                target=lambda: fastestPathRun(maze, robot, realRun, waypointRow, waypointCol),
                daemon=True)
            FPthread.start()

            simulator.run()

            # Reset waypoint
            waypointRow = None
            waypointCol = None
        # Exploration
        elif choice == 3 or choice == 4:
            scoreMaze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
            exploredMaze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
            explorationInit(scoreMaze, exploredMaze)

            timeLimit = 3600
            coverageLimit = 300
            speed = SPEED
            if choice == 3:
                realRun = False
            else:
                realRun = True
            robot = Robot(START_ROW, START_COL, realRun)
            simulator = Simulator(scoreMaze, robot)
            robot.setSimulator(simulator)
            robot.setSpeed(speed)

            if choice == 4:
                CommManager.connect()
                Helper.waitForCommand(CommandType.EX_START)

            # Start exploration in a new thread
            EXThread = Thread(
                target=lambda: Exploration(exploredMaze, maze, robot, simulator, timeLimit, coverageLimit,
                                           realRun).runExploration(),
                daemon=True)
            EXThread.start()

            simulator.run()
        # Image Finding
        elif choice == 5 or choice == 6:
            scoreMaze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
            exploredMaze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
            explorationInit(scoreMaze, exploredMaze)
            realImages = {(2, 7, Direction.LEFT), (4, 12, Direction.DOWN),
                          (10, 10, Direction.RIGHT), (14, 12, Direction.UP),
                          (13, 1, Direction.UP)}
            # realImages = {(2, 7, Direction.LEFT), (4, 12, Direction.DOWN),
            #               (10, 10, Direction.RIGHT), (14, 12, Direction.UP),
            #               }

            if choice == 5:
                realRun = False
            else:
                realRun = True

            robot = Robot(START_ROW, START_COL, realRun)
            simulator = Simulator(scoreMaze, robot)
            robot.setSimulator(simulator)

            if choice == 6:
                CommManager.connect()
                Helper.waitForCommand(CommandType.IF_START)

            # Start image finding in a new thread
            IFThread = Thread(
                target=lambda: ImageFinding(exploredMaze, maze, robot,
                                            simulator, 3600, 300, realRun, realImages).runImageFinding(),
                daemon=True)
            IFThread.start()

            simulator.run()

        printMenu()
        choice = int(input("Enter your choice: "))


def fastestPathRun(maze, robot, realRun, waypointRow, waypointCol):
    if waypointRow is not None and waypointCol is not None:
        FastestPath(maze, robot, waypointRow, waypointCol, realRun).runFastestPath()
    FastestPath(maze, robot, GOAL_ROW, GOAL_COL, realRun).runFastestPath()


def printMenu():
    print()
    print("1) Run simulated fastest path")
    print("2) Run real fastest path")
    print("3) Run simulated exploration")
    print("4) Run real exploration")
    print("5) Run simulated image finding")
    print("6) Run real image finding")


def fastestPathInit(maze, scoreMaze):
    for i in range(ROW_SIZE):
        for j in range(COL_SIZE):
            if maze[i][j].isObstacle:
                scoreMaze[i][j] = Color.OBSTACLE.value
            else:
                scoreMaze[i][j] = Color.EMPTY_CELL.value


def explorationInit(scoreMaze, exploredMaze):
    for i in range(ROW_SIZE):
        for j in range(COL_SIZE):
            scoreMaze[i][j] = Color.UNEXPLORED.value

    for i in range(ROW_SIZE):
        for j in range(COL_SIZE):
            exploredMaze[i][j] = Cell(i, j)
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            exploredMaze[START_ROW + dr][START_COL + dc].isExplored = True
            exploredMaze[GOAL_ROW + dr][GOAL_COL + dc].isExplored = True


def loadMazeFromMapDescriptorP2(hexP2):
    return MapDescriptor.convertToMaze(hexP2)


def loadMazeFromArenaFile():
    arena = loadArena()
    maze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
    for i in range(ROW_SIZE):
        for j in range(COL_SIZE):
            if arena[i][j] == 1:
                maze[ROW_SIZE - 1 - i][j] = Cell(ROW_SIZE - 1 - i, j, isObstacle=True)
            else:
                maze[ROW_SIZE - 1 - i][j] = Cell(ROW_SIZE - 1 - i, j, isObstacle=False)
            maze[ROW_SIZE - 1 - i][j].isExplored = True
    return maze


def printMaze(maze):
    for i in range(ROW_SIZE):
        for j in range(COL_SIZE):
            if maze[ROW_SIZE - 1 - i][j].isExplored:
                if maze[ROW_SIZE - 1 - i][j].isObstacle:
                    print("1", end=" ")
                else:
                    print("0", end=" ")
            else:
                print("X", end=" ")
        print()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
