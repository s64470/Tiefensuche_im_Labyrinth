import tkinter as tk
import random
import heapq

# Constants
CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 20
DELAY = 30
BACKGROUNDCOLOR = "#ffffff"
CURSORCOLOR = "#a9c6f5"


# Cell class definition
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


# Grid creation and utility
def create_grid():
    return [[Cell(x, y) for y in range(GRID_HEIGHT)] for x in range(GRID_WIDTH)]


def get_neighbors(grid, cell):
    neighbors = []
    directions = {"top": (0, -1), "right": (1, 0), "bottom": (0, 1), "left": (-1, 0)}
    for direction, (dx, dy) in directions.items():
        nx, ny = cell.x + dx, cell.y + dy
        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
            neighbor = grid[nx][ny]
            if not neighbor.visited:
                neighbors.append((direction, neighbor))
    return neighbors


def remove_walls(current, next_cell, direction):
    opposite = {"top": "bottom", "right": "left", "bottom": "top", "left": "right"}
    current.walls[direction] = False
    next_cell.walls[opposite[direction]] = False


# Heuristic for A*
def heuristic(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)


# A* solver
def a_star_solver(grid, start, goal, canvas):
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
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
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


# Reconstruct and show path
def reconstruct_path(came_from, current, canvas):
    while current in came_from:
        current = came_from[current]
        current.highlight(canvas, "green")
        canvas.update()
        canvas.after(DELAY)


# Main app class
class MazeApp:
    def __init__(self, root):
        self.canvas = tk.Canvas(
            root,
            width=GRID_WIDTH * CELL_SIZE,
            height=GRID_HEIGHT * CELL_SIZE,
            bg=BACKGROUNDCOLOR,
        )
        self.canvas.pack()
        self.grid = create_grid()
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
            neighbors = get_neighbors(self.grid, self.current)
            if neighbors:
                direction, next_cell = random.choice(neighbors)
                remove_walls(self.current, next_cell, direction)
                next_cell.visited = True
                self.stack.append(self.current)
                self.current = next_cell
            else:
                self.current = self.stack.pop()
            self.canvas.after(DELAY, self.step)
        elif not self.maze_generated:
            self.maze_generated = True
            start = self.grid[0][0]
            goal = self.grid[GRID_WIDTH - 1][GRID_HEIGHT - 1]
            a_star_solver(self.grid, start, goal, self.canvas)


# Launch GUI
def main():
    root = tk.Tk()
    root.title("Maze Generator with A* Solver")
    app = MazeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()