import tkinter

from ..static.Constants import CANVAS_WIDTH, CANVAS_HEIGHT, ROW_SIZE, \
    COL_SIZE, START_X, START_Y, GRID_WIDTH, colors, di, dj, START_ROW, START_COL, GOAL_ROW, GOAL_COL
from ..static.Color import Color
from ..static.Action import Action


class Simulator:

    def __init__(self, scoreMaze, maze, robot):
        self.window = tkinter.Tk()
        self.window.title('MDP Simulator')

        self.canvas = tkinter.Canvas(self.window, bg='white', height=CANVAS_HEIGHT, width=CANVAS_WIDTH)

        self.scoreMaze = scoreMaze
        self.maze = maze
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
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                self.scoreMaze[START_ROW + dr][START_COL + dc] = Color.START_ZONE.value
                self.scoreMaze[GOAL_ROW + dr][GOAL_COL + dc] = Color.GOAL_ZONE.value

        for i in range(ROW_SIZE):
            self.box_ids.append([])
            for j in range(COL_SIZE):
                self.box_ids[i].append(self.canvas.create_rectangle(
                    START_X + j * GRID_WIDTH,
                    START_Y + i * GRID_WIDTH,
                    START_X + (j + 1) * GRID_WIDTH,
                    START_Y + (i + 1) * GRID_WIDTH,
                    fill=colors[self.scoreMaze[i][j]]
                ))

        for dr in range(-1, 2):
            for dc in range(-1, 2):
                self.canvas.itemconfig(self.box_ids[START_ROW + dr][START_COL + dc], fill=colors[Color.ROBOT.value])
        # Facing
        self.canvas.itemconfig(self.box_ids[START_ROW][START_COL + 1], fill=colors[Color.FACING.value])

    def updateRobotPos(self, action):
        if action is None:
            return
        r = self.robot.curRow
        c = self.robot.curCol
        direction = self.robot.curDir
        if action == Action.TURN_LEFT:
            self.leftMoveUpdate(r, c, direction)
        elif action == Action.TURN_RIGHT:
            self.rightMoveUpdate(r, c, direction)
        elif action == Action.MOVE_FORWARD:
            self.upMoveUpdate(r, c, direction)
        elif action == Action.MOVE_BACKWARD:
            self.downMoveUpdate(r, c, direction)

    def leftMoveUpdate(self, r, c, direction):
        self.canvas.itemconfig(self.box_ids[r + di[direction.value]][c + dj[direction.value]],
                               fill=colors[Color.ROBOT.value])
        new_direction = (direction.value - 1) % 4
        self.canvas.itemconfig(self.box_ids[r + di[new_direction]][c + dj[new_direction]],
                               fill=colors[Color.FACING.value])

    def rightMoveUpdate(self, r, c, direction):
        self.canvas.itemconfig(self.box_ids[r + di[direction.value]][c + dj[direction.value]],
                               fill=colors[Color.ROBOT.value])
        new_direction = (direction.value + 1) % 4
        self.canvas.itemconfig(self.box_ids[r + di[new_direction]][c + dj[new_direction]],
                               fill=colors[Color.FACING.value])

    def upMoveUpdate(self, r, c, direction):
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

    def downMoveUpdate(self, r, c, direction):
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