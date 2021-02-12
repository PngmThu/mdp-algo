import os

from src.algorithms.Exploration import Exploration
from src.objects.Robot import Robot
from src.objects.Cell import Cell
from src.static.Constants import ROW_SIZE, COL_SIZE, GOAL_ROW, GOAL_COL, START_ROW, START_COL
from src.utils.Helper import Helper
from src.algorithms.FastestPath import FastestPath
from src.utils.Simulator import Simulator

fastestPathDone = False


def loadArena():
    file1 = open(os.path.join('arenas', "arena4.txt"), 'r')
    lines = file1.readlines()

    arena = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
    for i in range(len(lines)):
        for j in range(COL_SIZE):
            arena[i][j] = int(lines[i][j])

    file1.close()
    return arena


def runFastestPath(simulator, robot, maze, toGoal):
    global fastestPathDone
    if not toGoal:
        if simulator.waypointRow is None or simulator.waypointCol is None or not simulator.start:
            simulator.window.after(100, lambda: runFastestPath(simulator, robot, maze, False))
            return
        actions = FastestPath(maze, robot, simulator.waypointRow, simulator.waypointCol).runFastestPath()
    else:
        actions = FastestPath(maze, robot, GOAL_ROW, GOAL_COL).runFastestPath()
        fastestPathDone = True
    executeAction(simulator, robot, maze, actions, 0)


def executeAction(simulator, robot, maze, actions, index):
    global fastestPathDone

    if index < len(actions):
        simulator.updateRobotPos(actions[index])
        robot.move(actions[index])
        if index + 1 < len(actions):
            simulator.window.after(150, lambda: executeAction(simulator, robot, maze, actions, index + 1))
        else:
            if not fastestPathDone:
                runFastestPath(simulator, robot, maze, True)


def main():
    arena = loadArena()
    robot = Robot(START_ROW, START_COL)
    scoreMaze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
    for i in range(ROW_SIZE):
        for j in range(COL_SIZE):
            if arena[i][j] == 1:
                scoreMaze[i][j] = 1
            else:
                scoreMaze[i][j] = 0

    maze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
    for i in range(ROW_SIZE):
        for j in range(COL_SIZE):
            if scoreMaze[i][j] == 1:
                maze[i][j] = Cell(i, j, isObstacle=True)
            else:
                maze[i][j] = Cell(i, j, isObstacle=False)

    simulator = Simulator(scoreMaze, maze, robot)

    # runFastestPath(simulator, robot, maze, False)
    #
    # simulator.run()

    # Exploration
    exploredMaze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
    for i in range(ROW_SIZE):
        for j in range(COL_SIZE):
            exploredMaze[i][j] = Cell(i, j)
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            exploredMaze[START_ROW + dr][START_COL + dc].isExplored = True
            exploredMaze[GOAL_ROW + dr][GOAL_COL + dc].isExplored = True

    realMaze = Helper.init2dArray(ROW_SIZE, COL_SIZE, 0)
    for i in range(ROW_SIZE):
        for j in range(COL_SIZE):
            realMaze[i][j] = Cell(i, j)

    explorationAlgo = Exploration(exploredMaze, maze, robot, 300, 3600)
    explorationAlgo.runExploration()
    for i in range(ROW_SIZE):
        for j in range(COL_SIZE):
            if exploredMaze[i][j].isExplored:
                if exploredMaze[i][j].isObstacle:
                    print("1", end=" ")
                else:
                    print("0", end=" ")
            else:
                print("X", end=" ")
        print()



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()