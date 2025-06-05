# Depth-First Search for Maze Solving

import tkinter as tk
import random

# Constants
CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 20
DELAY = 30  # milliseconds between steps
BACKGROUNDCOLOR = "#ffffff"  # maze background color
CURSORCOLOR = "#a9c6f5"


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
        self.step()

    def step(self):
        if self.stack:
            self.canvas.delete("all")
            for col in self.grid:
                for cell in col:
                    cell.draw(self.canvas)
            self.current.highlight(self.canvas, CURSORCOLOR)

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


def main():
    root = tk.Tk()
    root.title("Animated Recursive Maze Generator")
    app = MazeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()