import tkinter as tk
from tkinter import messagebox
import random
import time
from collections import deque

CELL_SIZE = 35
ROWS = 10
COLS = 10
directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

class MazeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Adventure")
        self.root.configure(bg="lightyellow")
        self.setup_start_screen()

    def setup_start_screen(self):
        self.clear_window()
        bg = tk.Canvas(self.root, width=400, height=300, bg="lightblue")
        bg.pack()
        bg.create_text(200, 60, text="Maze Adventure", font=("Helvetica", 24, "bold"), fill="darkblue")
        bg.create_text(200, 120, text="Find the key and escape the maze!", font=("Helvetica", 14), fill="black")
        start_button = tk.Button(self.root, text="Start Game", font=("Helvetica", 16), bg="green", fg="white", command=self.show_instructions)
        bg.create_window(200, 200, window=start_button)

    def show_instructions(self):
        self.clear_window()
        instr_label = tk.Label(self.root, text="Instructions", font=("Helvetica", 18, "bold"), fg="darkred", bg="lightyellow")
        instr_label.pack(pady=10)
        instructions = (
    "1. Use W/A/S/D or Arrow Keys to move.\n"
    "2. Or use on-screen buttons below the maze.\n"
    "3. Avoid the Black blocks (walls).\n"
    "4. Collect the Orange key before reaching the Green goal.\n"
    "5. Press 'Solve Maze' to auto-solve using BFS.\n"
    "6. Click 'New Maze' to play again.\n"
    "7. In the maze:\n"
    "   - Red = Player\n"
    "   - Blue = Start\n"
    "   - Orange = Key\n"
    "   - Green = Goal\n"
    "   - Black = Wall\n"
    "   - White = Empty Cell\n"
    "   - Yellow = BFS Solved Path"
)
        instr_text = tk.Label(self.root, text=instructions, font=("Helvetica", 12), justify="left", bg="lightyellow")
        instr_text.pack(pady=10)

        button_frame = tk.Frame(self.root, bg="lightyellow")
        button_frame.pack(pady=10)
        continue_button = tk.Button(button_frame, text="Continue to Game", bg="green", fg="white", command=self.start_game)
        continue_button.pack(side="left", padx=10)
        back_button = tk.Button(button_frame, text="Back to Home", command=self.setup_start_screen)
        back_button.pack(side="left", padx=10)

    def start_game(self):
        self.clear_window()

        self.canvas = tk.Canvas(self.root, width=COLS*CELL_SIZE, height=ROWS*CELL_SIZE)
        self.canvas.pack()

        self.step_counter = 0
        self.start_time = None
        self.timer_running = False
        self.has_key = False

        info_frame = tk.Frame(self.root)
        info_frame.pack()
        self.timer_label = tk.Label(info_frame, text="Time: 0s")
        self.timer_label.pack()
        self.steps_label = tk.Label(info_frame, text="Steps: 0")
        self.steps_label.pack()

        controls_frame = tk.Frame(self.root)
        controls_frame.pack(pady=5)
        self.solve_button = tk.Button(controls_frame, text="Solve Maze", command=self.solve_maze)
        self.solve_button.pack(pady=2)
        self.new_maze_button = tk.Button(controls_frame, text="New Maze", command=self.generate_maze)
        self.new_maze_button.pack(pady=2)
        self.back_button = tk.Button(controls_frame, text="Back to Instructions", command=self.show_instructions)
        self.back_button.pack(pady=2)

        self.create_dpad_controls()

        self.generate_maze()
        self.bind_keys()
        self.update_timer()

    def create_dpad_controls(self):
        dpad_frame = tk.Frame(self.root)
        dpad_frame.pack(pady=10)

        tk.Label(dpad_frame, text="Manual Controls:").grid(row=0, column=1)
        tk.Button(dpad_frame, text="↑", width=3, command=lambda: self.move(-1, 0)).grid(row=1, column=1)
        tk.Button(dpad_frame, text="←", width=3, command=lambda: self.move(0, -1)).grid(row=2, column=0)
        tk.Button(dpad_frame, text="→", width=3, command=lambda: self.move(0, 1)).grid(row=2, column=2)
        tk.Button(dpad_frame, text="↓", width=3, command=lambda: self.move(1, 0)).grid(row=3, column=1)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def generate_maze(self):
        while True:
            self.maze = [[0 if random.random() > 0.3 else 1 for _ in range(COLS)] for _ in range(ROWS)]
            self.start = (0, 0)
            self.end = (ROWS-1, COLS-1)
            self.key = self.place_key()
            self.maze[self.start[0]][self.start[1]] = 0
            self.maze[self.end[0]][self.end[1]] = 0
            self.maze[self.key[0]][self.key[1]] = 0
            if self.path_exists():
                break

        self.player_pos = list(self.start)
        self.step_counter = 0
        self.start_time = time.time()
        self.timer_running = True
        self.has_key = False
        self.draw_maze()

    def path_exists(self):
        queue = deque([(self.start, False)])
        visited = set([(self.start, False)])

        while queue:
            (r, c), has_key = queue.popleft()
            if (r, c) == self.key:
                has_key = True
            if (r, c) == self.end and has_key:
                return True
            for dr, dc in directions:
                nr, nc = r+dr, c+dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and self.maze[nr][nc] == 0:
                    state = ((nr, nc), has_key)
                    if state not in visited:
                        visited.add(state)
                        queue.append(((nr, nc), has_key))
        return False

    def place_key(self):
        while True:
            r = random.randint(0, ROWS-1)
            c = random.randint(0, COLS-1)
            if (r, c) != self.start and (r, c) != self.end and self.maze[r][c] == 0:
                return (r, c)

    def draw_maze(self, path=[]):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                x1, y1 = c*CELL_SIZE, r*CELL_SIZE
                x2, y2 = x1+CELL_SIZE, y1+CELL_SIZE
                color = "white"
                if self.maze[r][c] == 1:
                    color = "black"
                elif (r, c) == tuple(self.player_pos):
                    color = "red"
                elif (r, c) == self.end:
                    color = "green"
                elif (r, c) == self.start:
                    color = "blue"
                elif (r, c) == self.key and not self.has_key:
                    color = "orange"
                elif (r, c) in path:
                    color = "yellow"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

    def bind_keys(self):
        self.root.bind("<w>", lambda e: self.move(-1, 0))
        self.root.bind("<s>", lambda e: self.move(1, 0))
        self.root.bind("<a>", lambda e: self.move(0, -1))
        self.root.bind("<d>", lambda e: self.move(0, 1))
        self.root.bind("<Up>", lambda e: self.move(-1, 0))
        self.root.bind("<Down>", lambda e: self.move(1, 0))
        self.root.bind("<Left>", lambda e: self.move(0, -1))
        self.root.bind("<Right>", lambda e: self.move(0, 1))

    def move(self, dr, dc):
        nr, nc = self.player_pos[0]+dr, self.player_pos[1]+dc
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            if self.maze[nr][nc] == 0:
                self.player_pos = [nr, nc]
                self.step_counter += 1
                self.steps_label.config(text=f"Steps: {self.step_counter}")
                if (nr, nc) == self.key:
                    self.has_key = True
                    messagebox.showinfo("Key Collected!", "You picked up the key!")
                if (nr, nc) == self.end:
                    if self.has_key:
                        self.timer_running = False
                        messagebox.showinfo("Congratulations!", f"You reached the goal in {self.step_counter} steps and {int(time.time() - self.start_time)} seconds!")
                    else:
                        messagebox.showwarning("Locked Goal", "The goal is locked! Find the key first.")
                self.draw_maze()
            else:
                messagebox.showinfo("Blocked!", "Oops! That's a wall. Try another direction.")

    def update_timer(self):
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Time: {elapsed}s")
        self.root.after(1000, self.update_timer)

    def solve_maze(self):
        queue = deque([(self.start, [self.start], False)])
        visited = set()
        visited.add((self.start, False))

        while queue:
            (r, c), path, has_key = queue.popleft()
            if (r, c) == self.key:
                has_key = True
            if (r, c) == self.end and has_key:
                self.has_key = True
                self.draw_maze(path)
                return
            for dr, dc in directions:
                nr, nc = r+dr, c+dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and self.maze[nr][nc] == 0:
                    state = ((nr, nc), has_key)
                    if state not in visited:
                        visited.add(state)
                        queue.append(((nr, nc), path + [(nr, nc)], has_key))
        messagebox.showwarning("No Path", "No path exists to the goal with key!")

if __name__ == '__main__':
    root = tk.Tk()
    game = MazeGame(root)
    root.mainloop()
