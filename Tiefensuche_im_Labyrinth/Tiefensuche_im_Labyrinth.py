import tkinter as tk
import random
import heapq
import time

from tkinter import ttk

# Constants used in maze generation
CELL_SIZE = 20  # Pixel size of each cell
DELAY = 30  # Delay in milliseconds between
# animation steps
BACKGROUNDCOLOR = "#ffffff"  # Canvas background color (white)
CURSORCOLOR = "#a9c6f5"  # Color to highlight current cell
# (light blue)
FONTSTYLE = "Arial"
FONTSIZE = "11"
global size_var


class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {"top": True, "right": True, "bottom": True, "left": True}
        self.visited = False

    def draw(self, canvas):
        x1, y1 = self.x * CELL_SIZE, self.y * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        if self.walls["top"]:
            canvas.create_line(x1, y1, x2, y1)
        if self.walls["right"]:
            canvas.create_line(x2, y1, x2, y2)
        if self.walls["bottom"]:
            canvas.create_line(x2, y2, x1, y2)
        if self.walls["left"]:
            canvas.create_line(x1, y2, x1, y1)

    def highlight(self, canvas, color="yellow"):
        x1, y1 = self.x * CELL_SIZE, self.y * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        canvas.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2, fill=color, outline="")

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)


def create_grid(width, height):
    return [[Cell(x, y) for y in range(height)] for x in range(width)]


def get_neighbors(grid, cell, width, height):
    neighbors = []
    directions = {"top": (0, -1), "right": (1, 0), "bottom": (0, 1), "left": (-1, 0)}
    for direction, (dx, dy) in directions.items():
        nx, ny = cell.x + dx, cell.y + dy
        if 0 <= nx < width and 0 <= ny < height:
            neighbor = grid[nx][ny]
            if not neighbor.visited:
                neighbors.append((direction, neighbor))
    return neighbors


def remove_walls(current, next_cell, direction):
    opposite = {"top": "bottom", "right": "left", "bottom": "top", "left": "right"}
    current.walls[direction] = False
    next_cell.walls[opposite[direction]] = False


def heuristic(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)


def a_star_solver(grid, start, goal, canvas, width, height):
    open_set = []
    heapq.heappush(open_set, (0, id(start), start))
    came_from = {}

    g_score = {cell: float("inf") for row in grid for cell in row}
    g_score[start] = 0

    f_score = {cell: float("inf") for row in grid for cell in row}
    f_score[start] = heuristic(start, goal)

    open_set_hash = {start}

    while open_set:
        _, __, current = heapq.heappop(open_set)
        open_set_hash.remove(current)

        if current == goal:
            reconstruct_path(came_from, current, canvas)
            return

        current.highlight(canvas, "gray")
        canvas.update()
        canvas.after(DELAY)

        for direction, (dx, dy) in {
            "top": (0, -1),
            "right": (1, 0),
            "bottom": (0, 1),
            "left": (-1, 0),
        }.items():
            if not current.walls[direction]:
                nx, ny = current.x + dx, current.y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    neighbor = grid[nx][ny]
                    temp_g_score = g_score[current] + 1
                    if temp_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = temp_g_score
                        f_score[neighbor] = temp_g_score + heuristic(neighbor, goal)
                        if neighbor not in open_set_hash:
                            heapq.heappush(
                                open_set, (f_score[neighbor], id(neighbor), neighbor)
                            )
                            open_set_hash.add(neighbor)
                            neighbor.highlight(canvas, "orange")
                            canvas.update()


def reconstruct_path(came_from, current, canvas):
    while current in came_from:
        current = came_from[current]
        current.highlight(canvas, "#b8cfc0")
        canvas.update()
        canvas.after(DELAY)


class MazeApp:
    def __init__(self, root, width, height):
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(
            root,
            width=width * CELL_SIZE,
            height=height * CELL_SIZE,
            bg=BACKGROUNDCOLOR,
        )
        self.canvas.pack()
        self.grid = create_grid(width, height)
        self.stack = []
        self.current = self.grid[0][0]
        self.current.visited = True
        self.stack.append(self.current)
        self.maze_generated = False
        self.step()

    def step(self):
        self.canvas.delete("all")
        for col in self.grid:
            for cell in col:
                cell.draw(self.canvas)

        self.current.highlight(self.canvas, CURSORCOLOR)

        if self.stack:
            neighbors = get_neighbors(self.grid, self.current, self.width, self.height)
            if neighbors:
                direction, next_cell = random.choice(neighbors)
                remove_walls(self.current, next_cell, direction)
                next_cell.visited = True
                self.stack.append(self.current)
                self.current = next_cell
            else:
                self.current = self.stack.pop()
            self.canvas.after(DELAY, self.step)
        # in MazeApp.step(), when maze is complete:
        elif not self.maze_generated:
            self.maze_generated = True
            start = self.grid[0][0]
            goal = self.grid[self.width - 1][self.height - 1]

            start_time = time.time()
            a_star_solver(self.grid, start, goal, self.canvas, self.width, self.height)
            end_time = time.time()

            print(f"A* Laufzeit: {end_time - start_time:.4f} Sekunden")


def start_maze(size_var):
    size = size_var.get()
    width = height = int(size)
    maze_width = width * CELL_SIZE
    maze_height = height * CELL_SIZE

    # Adjust window size
    x = (screen_width - maze_width) // 2
    y = (screen_height - maze_height) // 2
    root.geometry(f"{maze_width}x{maze_height}+{x}+{y}")

    # Remove previous widgets
    for widget in root.winfo_children():
        widget.destroy()

    MazeApp(root, width, height)


def main():
    global root, screen_width, screen_height, size_var

    root = tk.Tk()
    root.title("Maze Generator with A* Solver")
    root.resizable(False, False)

    # Set fixed size for the initial menu window
    initial_width = 400
    initial_height = 250

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - initial_width) // 2
    y = (screen_height - initial_height) // 2
    root.geometry(f"{initial_width}x{initial_height}+{x}+{y}")

    size_var = tk.StringVar(value="20")

    tk.Label(root, text="Select Maze Size:", font=(FONTSTYLE, FONTSIZE)).pack(
        pady=(20, 5)
    )

    # Create a horizontal frame for the radio buttons
    radio_frame = tk.Frame(root)
    radio_frame.pack(pady=(0, 10))

    # Pathfinding Algorithm
    algo_var = tk.StringVar(value="A*")  # Standard: A*

    tk.Label(
        root, text="Select Pathfinding Algorithm:", font=(FONTSTYLE, FONTSIZE)
    ).pack(pady=(20, 5))

    # Create a horizontal frame for the radio buttons
    algo_frame = tk.Frame(root)
    algo_frame.pack(pady=(0, 10))

    # Radio Buttons for selecting a pathfinding algorithm
    for algo in ["A*", "BFS"]:
        tk.Radiobutton(
            algo_frame,
            text=algo,
            variable=algo_var,
            value=algo,
            font=(FONTSTYLE, FONTSIZE),
            indicatoron=0,  # Makes them look like buttons instead of circles
            width=8,
            relief="raised",
            padx=5,
            pady=2,
        ).pack(side="left", padx=5)

    # Radio Buttons for selecting maze sizes
    for size in ["5", "10", "15", "20", "25", "30"]:
        tk.Radiobutton(
            radio_frame,
            text=size,
            variable=size_var,
            value=size,
            font=(FONTSTYLE, FONTSIZE),
            indicatoron=0,  # Makes them look like buttons instead of circles
            width=4,
            relief="raised",
            padx=5,
            pady=2,
        ).pack(side="left", padx=3)

    tk.Button(
        root,
        text="Start Maze",
        font=(FONTSTYLE, FONTSIZE),
        command=lambda: start_maze(size_var),
    ).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()