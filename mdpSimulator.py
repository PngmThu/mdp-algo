import tkinter
from tkinter import *

# --------------------------------------#

# 0: empty cell (white)
# 1: obstacle (blue)
# 2: start & goal zone (green)
# 3: robot (yellow)
# 4: facing direction of robot (orange)
colors = ['white', 'blue', 'green', 'yellow', 'orange']

# Up, right, down, left: 0, 1, 2, 3
di = [-1, 0, 1, 0]
dj = [0, 1, 0, -1]

arena = [
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
    [2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]]

box_ids = []


def setup():
    for i in range(20):
        box_ids.append([])
        for j in range(15):
            box_ids[i].append(C.create_rectangle(
                start_x + j * WIDTH,
                start_y + i * WIDTH,
                start_x + (j + 1) * WIDTH,
                start_y + (i + 1) * WIDTH,
                fill=colors[arena[i][j]],
                outline="blue",
                width=2))
    C.itemconfig(box_ids[17][0], fill=colors[3])
    C.itemconfig(box_ids[18][0], fill=colors[3])
    C.itemconfig(box_ids[19][0], fill=colors[3])
    C.itemconfig(box_ids[17][1], fill=colors[3])
    C.itemconfig(box_ids[18][1], fill=colors[3])
    C.itemconfig(box_ids[19][1], fill=colors[3])
    C.itemconfig(box_ids[17][2], fill=colors[3])
    C.itemconfig(box_ids[18][2], fill=colors[4])
    C.itemconfig(box_ids[19][2], fill=colors[3])
    print(box_ids)


def is_valid_move(new_r, new_c):
    if (new_r - 1 < 0) or (new_r + 1 >= 20) or (new_c - 1 < 0) or (new_c + 1 >= 15):
        return False

    for i in range(new_r - 1, new_r + 2):
        for j in range(new_c - 1, new_c + 2):
            if arena[i][j] == 1:
                return False
    return True


class SimulatedRobot:

    def __init__(self):
        self.r = 18
        self.c = 1
        self.pointing = 1  # 0 is up, 1 is right, 2 is down, 3 is left

    def move(self, move_direction):
        if move_direction == "Left":
            C.itemconfig(box_ids[self.r + di[self.pointing]][self.c + dj[self.pointing]], fill=colors[3])
            self.pointing = (self.pointing - 1) % 4
            C.itemconfig(box_ids[self.r + di[self.pointing]][self.c + dj[self.pointing]], fill=colors[4])
        elif move_direction == "Right":
            C.itemconfig(box_ids[self.r + di[self.pointing]][self.c + dj[self.pointing]], fill=colors[3])
            self.pointing = (self.pointing + 1) % 4
            C.itemconfig(box_ids[self.r + di[self.pointing]][self.c + dj[self.pointing]], fill=colors[4])
        elif move_direction == "Up":
            new_r = self.r + di[self.pointing]
            new_c = self.c + dj[self.pointing]
            if is_valid_move(new_r, new_c):
                if di[self.pointing] != 0:
                    set_r = self.r + di[self.pointing] * 2
                    # Set next move and pointing color
                    C.itemconfig(box_ids[set_r][self.c - 1], fill=colors[3])
                    C.itemconfig(box_ids[set_r][self.c], fill=colors[4])
                    C.itemconfig(box_ids[set_r][self.c + 1], fill=colors[3])
                    # Set previous pointing to robot color
                    C.itemconfig(box_ids[self.r + di[self.pointing]][self.c], fill=colors[3])

                    # Clear previous position
                    clear_r = self.r - di[self.pointing]
                    C.itemconfig(box_ids[clear_r][self.c - 1], fill=colors[arena[clear_r][self.c - 1]])
                    C.itemconfig(box_ids[clear_r][self.c], fill=colors[arena[clear_r][self.c]])
                    C.itemconfig(box_ids[clear_r][self.c + 1], fill=colors[arena[clear_r][self.c + 1]])
                elif dj[self.pointing] != 0:
                    set_c = self.c + dj[self.pointing] * 2
                    # Set next move and pointing color
                    C.itemconfig(box_ids[self.r - 1][set_c], fill=colors[3])
                    C.itemconfig(box_ids[self.r][set_c], fill=colors[4])
                    C.itemconfig(box_ids[self.r + 1][set_c], fill=colors[3])

                    # Set previous pointing to robot color
                    C.itemconfig(box_ids[self.r][self.c + dj[self.pointing]], fill=colors[3])

                    # Clear previous position
                    clear_c = self.c - dj[self.pointing]
                    C.itemconfig(box_ids[self.r - 1][clear_c], fill=colors[arena[self.r - 1][clear_c]])
                    C.itemconfig(box_ids[self.r][clear_c], fill=colors[arena[self.r][clear_c]])
                    C.itemconfig(box_ids[self.r + 1][clear_c], fill=colors[arena[self.r + 1][clear_c]])
                self.r = new_r
                self.c = new_c
        elif move_direction == "Down":
            new_r = self.r - di[self.pointing]
            new_c = self.c - dj[self.pointing]
            if is_valid_move(new_r, new_c):
                if di[self.pointing] != 0:
                    # Set backward move
                    set_r = self.r - di[self.pointing] * 2
                    C.itemconfig(box_ids[set_r][self.c - 1], fill=colors[3])
                    C.itemconfig(box_ids[set_r][self.c], fill=colors[3])
                    C.itemconfig(box_ids[set_r][self.c + 1], fill=colors[3])

                    # Set pointing
                    C.itemconfig(box_ids[self.r][self.c], fill=colors[4])

                    # clear previous position
                    clear_r = self.r + di[self.pointing]
                    C.itemconfig(box_ids[clear_r][self.c - 1], fill=colors[arena[clear_r][self.c - 1]])
                    C.itemconfig(box_ids[clear_r][self.c], fill=colors[arena[clear_r][self.c]])
                    C.itemconfig(box_ids[clear_r][self.c + 1], fill=colors[arena[clear_r][self.c + 1]])
                elif dj[self.pointing] != 0:
                    # Set backward move
                    set_c = self.c - dj[self.pointing] * 2
                    C.itemconfig(box_ids[self.r - 1][set_c], fill=colors[3])
                    C.itemconfig(box_ids[self.r][set_c], fill=colors[3])
                    C.itemconfig(box_ids[self.r + 1][set_c], fill=colors[3])

                    # Set pointing
                    C.itemconfig(box_ids[self.r][self.c], fill=colors[4])

                    # clear previous position
                    clear_c = self.c + dj[self.pointing]
                    C.itemconfig(box_ids[self.r - 1][clear_c], fill=colors[arena[self.r - 1][clear_c]])
                    C.itemconfig(box_ids[self.r][clear_c], fill=colors[arena[self.r][clear_c]])
                    C.itemconfig(box_ids[self.r + 1][clear_c], fill=colors[arena[self.r + 1][clear_c]])
                self.r = new_r
                self.c = new_c


simulatedRobot = SimulatedRobot()

# --------------------------------------#

window = tkinter.Tk()
window.title('MDP Simulator')


# --------------------------------------#

def interaction(event, start=False):
    if not start:
        print("Key Pressed:", event.keysym)
        move_direction = event.keysym
        simulatedRobot.move(move_direction)


# window.bind("<Key>", paint)
window.bind("<Key>", interaction)

# --------------------------------------#

H = 700
W = 600

C = Canvas(window, bg="white", height=H, width=W)

start_x, start_y = 50, 50
WIDTH = 30

# paint(None, start=True)
setup()

message = Label(window, text="Use the Arrow Keys to Move")
message.pack(side=BOTTOM)

C.pack()
window.mainloop()
