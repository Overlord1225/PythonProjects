import random
import tkinter as tk
from tkinter import messagebox

# ========== GAME LOGIC ==========
SIZE = 4

def reset_board():
    """Create a new 4x4 board with two starting tiles."""
    board = [[0] * SIZE for _ in range(SIZE)]
    add_new_tile(board)
    add_new_tile(board)
    return board

def add_new_tile(board):
    """Place a 2 (90%) or 4 (10%) in a random empty cell."""
    empty = [(r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c] == 0]
    if empty:
        r, c = random.choice(empty)
        board[r][c] = 2 if random.random() < 0.9 else 4

def slide_left(row):
    """
    Slide a single row left, merge equal tiles, and return (new_row, score_gained).
    """
    # Remove zeros
    non_zero = [x for x in row if x != 0]
    merged = []
    score = 0
    skip = False
    for i in range(len(non_zero)):
        if skip:
            skip = False
            continue
        if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
            merged.append(non_zero[i] * 2)
            score += non_zero[i] * 2      # add merged value to score
            skip = True
        else:
            merged.append(non_zero[i])
    # Pad with zeros
    merged += [0] * (SIZE - len(merged))
    return merged, score

def move_left(board):
    """Apply left slide to every row, return new board and total score."""
    new_board = []
    total_score = 0
    for row in board:
        new_row, score = slide_left(row)
        new_board.append(new_row)
        total_score += score
    return new_board, total_score

def move_right(board):
    """Reverse rows, slide left, reverse back."""
    new_board = []
    total_score = 0
    for row in board:
        rev = row[::-1]
        slid, score = slide_left(rev)
        new_board.append(slid[::-1])
        total_score += score
    return new_board, total_score

def transpose(board):
    """Transpose the 4x4 matrix."""
    return [[board[r][c] for r in range(SIZE)] for c in range(SIZE)]

def move_up(board):
    """Transpose, slide left, transpose back."""
    t = transpose(board)
    new_t, score = move_left(t)
    return transpose(new_t), score

def move_down(board):
    """Transpose, slide right, transpose back."""
    t = transpose(board)
    new_t, score = move_right(t)
    return transpose(new_t), score

def is_game_over(board):
    """Return True if no moves are possible."""
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                return False
            if c + 1 < SIZE and board[r][c + 1] == board[r][c]:
                return False
            if r + 1 < SIZE and board[r + 1][c] == board[r][c]:
                return False
    return True

def has_won(board):
    """Check if any tile equals 2048."""
    return any(2048 in row for row in board)

# ========== GUI COLORS ==========
TILE_COLORS = {
    0:    "#cdc1b4",
    2:    "#eee4da",
    4:    "#ede0c8",
    8:    "#f2b179",
    16:   "#f59563",
    32:   "#f67c5f",
    64:   "#f65e3b",
    128:  "#edcf72",
    256:  "#edcc61",
    512:  "#edc850",
    1024: "#edc53f",
    2048: "#edc22e",
}

TILE_TEXT_COLORS = {
    0:    "#cdc1b4",
    2:    "#776e65",
    4:    "#776e65",
    8:    "#f9f6f2",
    16:   "#f9f6f2",
    32:   "#f9f6f2",
    64:   "#f9f6f2",
    128:  "#f9f6f2",
    256:  "#f9f6f2",
    512:  "#f9f6f2",
    1024: "#f9f6f2",
    2048: "#f9f6f2",
}

def get_tile_color(value):
    return TILE_COLORS.get(value, "#3c3a32")

def get_text_color(value):
    return TILE_TEXT_COLORS.get(value, "#f9f6f2")

# ========== GUI APPLICATION ==========
class Game2048GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("2048")
        self.root.resizable(False, False)
        self.root.configure(bg="#bbada0")

        # Score label
        self.score_var = tk.StringVar(value="Score: 0")
        score_label = tk.Label(
            root,
            textvariable=self.score_var,
            font=("Helvetica", 16, "bold"),
            bg="#bbada0",
            fg="#776e65"
        )
        score_label.grid(row=0, column=0, columnspan=SIZE, pady=(10, 5))

        # Board frame
        self.board_frame = tk.Frame(root, bg="#bbada0")
        self.board_frame.grid(row=1, column=0, padx=10, pady=5)

        # Tile grid (Labels)
        self.tiles = []
        for r in range(SIZE):
            row_tiles = []
            for c in range(SIZE):
                cell = tk.Label(
                    self.board_frame,
                    text="",
                    font=("Helvetica", 28, "bold"),
                    width=4,
                    height=2,
                    bg="#cdc1b4",
                    relief="flat"
                )
                cell.grid(row=r, column=c, padx=5, pady=5)
                row_tiles.append(cell)
            self.tiles.append(row_tiles)

        # New Game button
        new_game_btn = tk.Button(
            root,
            text="New Game",
            font=("Helvetica", 12, "bold"),
            bg="#8f7a66",
            fg="#f9f6f2",
            relief="flat",
            padx=20,
            pady=5,
            command=self.new_game
        )
        new_game_btn.grid(row=2, column=0, pady=(5, 10))

        # Keyboard bindings
        root.bind("<Up>", lambda e: self.move("up"))
        root.bind("<Down>", lambda e: self.move("down"))
        root.bind("<Left>", lambda e: self.move("left"))
        root.bind("<Right>", lambda e: self.move("right"))
        root.bind("<w>", lambda e: self.move("up"))
        root.bind("<s>", lambda e: self.move("down"))
        root.bind("<a>", lambda e: self.move("left"))
        root.bind("<d>", lambda e: self.move("right"))

        # Start the game
        self.new_game()

    def new_game(self):
        """Reset board and score."""
        self.board = reset_board()
        self.score = 0
        self.update_display()

    def update_display(self):
        """Refresh all tile labels and the score."""
        for r in range(SIZE):
            for c in range(SIZE):
                value = self.board[r][c]
                self.tiles[r][c].config(
                    text=str(value) if value != 0 else "",
                    bg=get_tile_color(value),
                    fg=get_text_color(value)
                )
        self.score_var.set(f"Score: {self.score}")

    def move(self, direction):
        """Perform a move if valid, then check win/lose."""
        moves = {
            "left": move_left,
            "right": move_right,
            "up": move_up,
            "down": move_down,
        }

        old_board = [row[:] for row in self.board]
        new_board, gained = moves[direction](self.board)

        # Only proceed if the board actually changed
        if new_board != old_board:
            self.board = new_board
            self.score += gained
            add_new_tile(self.board)
            self.update_display()

            if has_won(self.board):
                messagebox.showinfo("🎉 Congratulations!", "You reached 2048!")
            elif is_game_over(self.board):
                messagebox.showinfo("💀 Game Over", f"Final score: {self.score}")

# ========== RUN THE GAME ==========
if __name__ == "__main__":
    root = tk.Tk()
    app = Game2048GUI(root)
    root.mainloop()