import tkinter

from .Helper import Helper
from ..static.Constants import CANVAS_WIDTH, CANVAS_HEIGHT, ROW_SIZE, \
    COL_SIZE, START_X, START_Y, GRID_WIDTH, colors, di, dj, START_ROW, \
    START_COL, GOAL_ROW, GOAL_COL, CIRCLE_X, CIRCLE_Y, CIRCLE_RADIUS
from ..static.Color import Color
from ..static.Action import Action
from ..static.Direction import Direction


class Simulator:

    def __init__(self, scoreMaze, robot):
        self.window = tkinter.Tk()
        self.window.title('MDP Simulator')

        self.canvas = tkinter.Canvas(self.window, bg='white', height=CANVAS_HEIGHT, width=CANVAS_WIDTH)

        self.scoreMaze = scoreMaze
        self.robot = robot
        self.box_ids = []
        self.start = False
        self.waypointRow = None
        self.waypointCol = None

        self.textBox1 = None
        self.textBox2 = None
        self.setupMenu()

        self.setupLayout()
        self.canvas.pack()

    def run(self):
        self.window.mainloop()

    def clickStartButton(self):
        self.start = True

    def retrieveInputs(self):
        if self.waypointRow is not None and self.waypointCol is not None:
            self.canvas.itemconfig(self.box_ids[self.waypointRow][self.waypointCol], fill=colors[Color.EMPTY_CELL.value])
            self.scoreMaze[self.waypointRow][self.waypointCol] = 0
        if self.textBox1.get("1.0", "end-1c") == "" or self.textBox2.get("1.0", "end-1c") == "":
            print("Please input again!")
            return
        self.waypointRow = int(self.textBox1.get("1.0", "end-1c"))
        self.waypointCol = int(self.textBox2.get("1.0", "end-1c"))
        print("Waypoint:", self.waypointRow, self.waypointCol)
        if 0 <= self.waypointRow < ROW_SIZE and 0 <= self.waypointCol < COL_SIZE and self.scoreMaze[self.waypointRow][self.waypointCol] != 1:
            self.canvas.itemconfig(self.box_ids[self.waypointRow][self.waypointCol], fill=colors[Color.WAYPOINT.value])
            self.scoreMaze[self.waypointRow][self.waypointCol] = Color.WAYPOINT.value
        else:
            self.waypointRow = None
            self.waypointCol = None
            print("Way point is set at an obstacle or out of bound! Please input again!")

    def setupMenu(self):
        label2 = tkinter.Label(self.window, text="wp-r:")
        label2.pack(side=tkinter.LEFT)
        self.textBox1 = tkinter.Text(self.window, height=1, width=10)
        self.textBox1.pack(side=tkinter.LEFT, padx=2, pady=2)

        label3 = tkinter.Label(self.window, text="wp-c:")
        label3.pack(side=tkinter.LEFT)
        self.textBox2 = tkinter.Text(self.window, height=1, width=10)
        self.textBox2.pack(side=tkinter.LEFT, padx=2, pady=2)

        buttonCommit = tkinter.Button(self.window, height=1, width=10, text="Submit!",
                                      command=lambda: self.retrieveInputs())
        buttonCommit.pack(side=tkinter.LEFT, padx=2, pady=2)

        button = tkinter.Button(self.window, text='Start!', command=lambda: self.clickStartButton())
        button.pack(side=tkinter.LEFT, padx=2, pady=2)

    # Draw cells and color them
    def setupLayout(self):
        # Color for start and goal zone
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                self.scoreMaze[START_ROW + dr][START_COL + dc] = Color.START_ZONE.value
                self.scoreMaze[GOAL_ROW + dr][GOAL_COL + dc] = Color.GOAL_ZONE.value

        for i in range(ROW_SIZE):
            self.box_ids.append([])
            for j in range(COL_SIZE):
                self.box_ids[i].append(self.canvas.create_rectangle(
                    START_X + j * GRID_WIDTH,
                    START_Y - i * GRID_WIDTH,
                    START_X + (j + 1) * GRID_WIDTH,
                    START_Y - (i + 1) * GRID_WIDTH,
                    fill=colors[self.scoreMaze[i][j]]
                ))

        for dr in range(-1, 2):
            for dc in range(-1, 2):
                self.canvas.itemconfig(self.box_ids[START_ROW + dr][START_COL + dc], fill=colors[Color.ROBOT.value])
        # Facing: Up
        self.canvas.itemconfig(self.box_ids[START_ROW + 1][START_COL], fill=colors[Color.FACING.value])

        # self.drawImageSticker(6, 0, Direction.DOWN)
        # self.drawImageSticker(2, 7, Direction.LEFT)

    def updateRobotPos(self, action):
        if action is None:
            return
        r = self.robot.curRow
        c = self.robot.curCol
        direction = self.robot.curDir
        if action == Action.TURN_LEFT:
            self.turnLeftUpdate(r, c, direction)
        elif action == Action.TURN_RIGHT:
            self.turnRightUpdate(r, c, direction)
        elif action == Action.MOVE_FORWARD:
            self.moveForwardUpdate(r, c, direction)
        elif action == Action.MOVE_BACKWARD:
            self.moveBackwardUpdate(r, c, direction)

    def turnLeftUpdate(self, r, c, direction):
        self.canvas.itemconfig(self.box_ids[r + di[direction.value]][c + dj[direction.value]],
                               fill=colors[Color.ROBOT.value])
        new_direction = Helper.previousDir(direction)
        self.canvas.itemconfig(self.box_ids[r + di[new_direction.value]][c + dj[new_direction.value]],
                               fill=colors[Color.FACING.value])

    def turnRightUpdate(self, r, c, direction):
        self.canvas.itemconfig(self.box_ids[r + di[direction.value]][c + dj[direction.value]],
                               fill=colors[Color.ROBOT.value])
        new_direction = Helper.nextDir(direction)
        self.canvas.itemconfig(self.box_ids[r + di[new_direction.value]][c + dj[new_direction.value]],
                               fill=colors[Color.FACING.value])

    def moveForwardUpdate(self, r, c, direction):
        # Up or down
        if di[direction.value] != 0:
            set_r = r + di[direction.value] * 2
            # Set next move and pointing color
            self.canvas.itemconfig(self.box_ids[set_r][c - 1], fill=colors[Color.ROBOT.value])
            self.canvas.itemconfig(self.box_ids[set_r][c], fill=colors[Color.FACING.value])
            self.canvas.itemconfig(self.box_ids[set_r][c + 1], fill=colors[Color.ROBOT.value])
            # Set previous pointing to robot color
            self.canvas.itemconfig(self.box_ids[r + di[direction.value]][c], fill=colors[Color.ROBOT.value])

            # Clear previous position
            clear_r = r - di[direction.value]
            self.canvas.itemconfig(self.box_ids[clear_r][c - 1], fill=colors[self.scoreMaze[clear_r][c - 1]])
            self.canvas.itemconfig(self.box_ids[clear_r][c], fill=colors[self.scoreMaze[clear_r][c]])
            self.canvas.itemconfig(self.box_ids[clear_r][c + 1], fill=colors[self.scoreMaze[clear_r][c + 1]])
        # Left or right
        elif dj[direction.value] != 0:
            set_c = c + dj[direction.value] * 2
            # Set next move and pointing color
            self.canvas.itemconfig(self.box_ids[r - 1][set_c], fill=colors[Color.ROBOT.value])
            self.canvas.itemconfig(self.box_ids[r][set_c], fill=colors[Color.FACING.value])
            self.canvas.itemconfig(self.box_ids[r + 1][set_c], fill=colors[Color.ROBOT.value])

            # Set previous pointing to robot color
            self.canvas.itemconfig(self.box_ids[r][c + dj[direction.value]], fill=colors[Color.ROBOT.value])

            # Clear previous position
            clear_c = c - dj[direction.value]
            self.canvas.itemconfig(self.box_ids[r - 1][clear_c], fill=colors[self.scoreMaze[r - 1][clear_c]])
            self.canvas.itemconfig(self.box_ids[r][clear_c], fill=colors[self.scoreMaze[r][clear_c]])
            self.canvas.itemconfig(self.box_ids[r + 1][clear_c], fill=colors[self.scoreMaze[r + 1][clear_c]])

    def moveBackwardUpdate(self, r, c, direction):
        if di[direction.value] != 0:
            # Set backward move
            set_r = r - di[direction.value] * 2
            self.canvas.itemconfig(self.box_ids[set_r][c - 1], fill=colors[Color.ROBOT.value])
            self.canvas.itemconfig(self.box_ids[set_r][c], fill=colors[Color.ROBOT.value])
            self.canvas.itemconfig(self.box_ids[set_r][c + 1], fill=colors[Color.ROBOT.value])

            # Set pointing
            self.canvas.itemconfig(self.box_ids[r][c], fill=colors[Color.FACING.value])

            # clear previous position
            clear_r = r + di[direction.value]
            self.canvas.itemconfig(self.box_ids[clear_r][c - 1], fill=colors[self.scoreMaze[clear_r][c - 1]])
            self.canvas.itemconfig(self.box_ids[clear_r][c], fill=colors[self.scoreMaze[clear_r][c]])
            self.canvas.itemconfig(self.box_ids[clear_r][c + 1], fill=colors[self.scoreMaze[clear_r][c + 1]])
        elif dj[direction.value] != 0:
            # Set backward move
            set_c = c - dj[direction.value] * 2
            self.canvas.itemconfig(self.box_ids[r - 1][set_c], fill=colors[Color.ROBOT.value])
            self.canvas.itemconfig(self.box_ids[r][set_c], fill=colors[Color.ROBOT.value])
            self.canvas.itemconfig(self.box_ids[r + 1][set_c], fill=colors[Color.ROBOT.value])

            # Set pointing
            self.canvas.itemconfig(self.box_ids[r][c], fill=colors[Color.FACING.value])

            # clear previous position
            clear_c = c + dj[direction.value]
            self.canvas.itemconfig(self.box_ids[r - 1][clear_c], fill=colors[self.scoreMaze[r - 1][clear_c]])
            self.canvas.itemconfig(self.box_ids[r][clear_c], fill=colors[self.scoreMaze[r][clear_c]])
            self.canvas.itemconfig(self.box_ids[r + 1][clear_c], fill=colors[self.scoreMaze[r + 1][clear_c]])

    def paintCell(self, row, col, color):
        if Helper.inStartZone(row, col) or Helper.inGoalZone(row, col):
            return
        self.scoreMaze[row][col] = color.value
        self.canvas.itemconfig(self.box_ids[row][col], fill=colors[color.value])

    def create_circle(self, x, y, r, **kwargs):
        return self.canvas.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def drawImageSticker(self, row, col, direction):
        self.create_circle(CIRCLE_X + col * GRID_WIDTH + GRID_WIDTH / 2 * dj[direction.value],
                           CIRCLE_Y - row * GRID_WIDTH - GRID_WIDTH / 2 * di[direction.value],
                           CIRCLE_RADIUS, fill=colors[Color.IMAGE.value])

    def setWayPoint(self, row, col):
        if 0 <= row < ROW_SIZE and 0 <= col < COL_SIZE and self.scoreMaze[row][col] != 1:
            self.canvas.itemconfig(self.box_ids[row][col], fill=colors[Color.WAYPOINT.value])
            self.scoreMaze[row][col] = Color.WAYPOINT.value
            return True
        return False

    def removeWayPoint(self, row, col):
        if 0 <= row < ROW_SIZE and 0 <= col < COL_SIZE and self.scoreMaze[row][col] == Color.WAYPOINT.value:
            self.canvas.itemconfig(self.box_ids[row][row], fill=colors[Color.EMPTY_CELL.value])
            self.scoreMaze[self.waypointRow][self.waypointCol] = 0
            return True
        return False

