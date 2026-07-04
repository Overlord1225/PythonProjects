# chess_app.py
# Tkinter GUI with main menu and "Return to Menu" option

import tkinter as tk
from tkinter import messagebox, ttk
import time

from chess_engine import ChessGame, BOARD_SIZE, PIECE_SYMBOLS, get_piece_color, enemy_color, in_bounds, square_name
from chess_ai import ChessAI

# --- Constants for UI ---
SQUARE_SIZE = 70
BOARD_PIXELS = BOARD_SIZE * SQUARE_SIZE
COORDINATE_SIZE = 20
TOTAL_WIDTH = BOARD_PIXELS + 2 * COORDINATE_SIZE
TOTAL_HEIGHT = BOARD_PIXELS + 2 * COORDINATE_SIZE


class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")
        self.game = ChessGame()
        self.ai = ChessAI(depth=4, time_limit=2.0)
        self.mode = None
        self.game_over = False
        self.selected = None
        self.legal_moves_for_selected = []
        self.startup = True   # prevents drawing before mode chosen

        # Menu
        menubar = tk.Menu(root)
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.new_game)
        game_menu.add_separator()
        game_menu.add_command(label="Play vs AI (White)", command=lambda: self.set_mode('human_white'))
        game_menu.add_command(label="Play vs AI (Black)", command=lambda: self.set_mode('human_black'))
        game_menu.add_command(label="Human vs Human", command=lambda: self.set_mode('human_vs_human'))
        game_menu.add_separator()
        game_menu.add_command(label="Return to Main Menu", command=self.return_to_menu)
        menubar.add_cascade(label="Game", menu=game_menu)
        root.config(menu=menubar)

        # Main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.LEFT, padx=5)
        self.canvas = tk.Canvas(canvas_frame, width=TOTAL_WIDTH, height=TOTAL_HEIGHT,
                                bg='white', highlightthickness=0)
        self.canvas.pack()

        # Right panel
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        ttk.Label(right_frame, text="Move History", font=('Arial', 12, 'bold')).pack(pady=5)
        self.move_listbox = tk.Listbox(right_frame, height=20, width=30)
        self.move_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        button_frame = ttk.Frame(right_frame)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="Undo", command=self.undo_move).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="New Game", command=self.new_game).pack(side=tk.LEFT, padx=2)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Select mode from the main menu")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.bind("<Button-1>", self.on_click)

        # Show main menu after a tiny delay
        self.root.after(100, self.show_start_menu)

    def show_start_menu(self):
        """Pop up a modal menu to choose the game mode."""
        top = tk.Toplevel(self.root)
        top.title("Chess - Main Menu")
        top.geometry("300x200")
        top.transient(self.root)
        top.grab_set()
        top.resizable(False, False)

        # Center the window
        top.update_idletasks()
        width = top.winfo_width()
        height = top.winfo_height()
        x = (top.winfo_screenwidth() // 2) - (width // 2)
        y = (top.winfo_screenheight() // 2) - (height // 2)
        top.geometry(f'+{x}+{y}')

        label = tk.Label(top, text="Choose your side", font=('Arial', 14, 'bold'))
        label.pack(pady=20)

        def select_mode(mode):
            top.destroy()
            self.set_mode(mode)

        btn_white = tk.Button(top, text="Play as White", width=20,
                              command=lambda: select_mode('human_white'))
        btn_white.pack(pady=5)

        btn_black = tk.Button(top, text="Play as Black", width=20,
                              command=lambda: select_mode('human_black'))
        btn_black.pack(pady=5)

        btn_human = tk.Button(top, text="Human vs Human", width=20,
                              command=lambda: select_mode('human_vs_human'))
        btn_human.pack(pady=5)

        # If user closes the window without choosing, just stay in startup mode
        top.protocol("WM_DELETE_WINDOW", lambda: self.close_menu(top))

    def close_menu(self, top):
        top.destroy()
        self.startup = True
        self.status_var.set("No game selected – use Game menu to start")

    def return_to_menu(self):
        """Return to the main menu, discarding current game."""
        self.startup = True
        self.game_over = True
        self.selected = None
        self.legal_moves_for_selected = []
        self.canvas.delete("all")
        self.move_listbox.delete(0, tk.END)
        self.status_var.set("Returning to main menu...")
        # Show the menu again
        self.show_start_menu()

    def set_mode(self, mode):
        self.mode = mode
        self.startup = False
        self.game_over = False
        self.new_game()
        self.status_var.set("Ready")
        if mode == 'human_black':
            self.root.after(500, self.do_ai_move)

    def new_game(self):
        self.game.reset()
        self.selected = None
        self.legal_moves_for_selected = []
        self.game_over = False
        self.draw_board()
        self.update_move_list()
        self.status_var.set("Ready")
        if self.mode == 'human_black':
            self.root.after(500, self.do_ai_move)

    # --- Drawing ---
    def draw_board(self):
        if self.startup:
            return   # don't draw until a mode is chosen
        self.canvas.delete("all")
        offset = COORDINATE_SIZE

        # Coordinates
        for c in range(BOARD_SIZE):
            x = offset + c * SQUARE_SIZE + SQUARE_SIZE // 2
            y = offset + BOARD_PIXELS + 10
            self.canvas.create_text(x, y, text=chr(ord('a') + c), font=('Arial', 10))
            y = offset - 10
            self.canvas.create_text(x, y, text=chr(ord('a') + c), font=('Arial', 10))
        for r in range(BOARD_SIZE):
            x = offset - 10
            y = offset + r * SQUARE_SIZE + SQUARE_SIZE // 2
            self.canvas.create_text(x, y, text=str(BOARD_SIZE - r), font=('Arial', 10))
            x = offset + BOARD_PIXELS + 10
            self.canvas.create_text(x, y, text=str(BOARD_SIZE - r), font=('Arial', 10))

        # Squares
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x1 = offset + c * SQUARE_SIZE
                y1 = offset + r * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE
                color = "#F0D9B5" if (r + c) % 2 == 0 else "#B58863"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        # Highlight selected
        if self.selected:
            r, c = self.selected
            x1 = offset + c * SQUARE_SIZE
            y1 = offset + r * SQUARE_SIZE
            x2 = x1 + SQUARE_SIZE
            y2 = y1 + SQUARE_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=4)

        # Legal moves
        for r, c in self.legal_moves_for_selected:
            x = offset + c * SQUARE_SIZE + SQUARE_SIZE // 2
            y = offset + r * SQUARE_SIZE + SQUARE_SIZE // 2
            self.canvas.create_oval(x - 8, y - 8, x + 8, y + 8, fill="green", outline="")

        # Pieces
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.game.board[r][c]
                if piece:
                    x = offset + c * SQUARE_SIZE + SQUARE_SIZE // 2
                    y = offset + r * SQUARE_SIZE + SQUARE_SIZE // 2
                    self.canvas.create_text(x, y, text=PIECE_SYMBOLS[piece],
                                            font=("Arial Unicode MS", int(SQUARE_SIZE * 0.6)),
                                            fill="black" if piece[0] == 'b' else "white")

        self.root.title(f"Chess - {self.game.current_player.upper()} to move")

    def update_move_list(self):
        self.move_listbox.delete(0, tk.END)
        moves = self.game.move_history
        for i in range(0, len(moves), 2):
            w = moves[i]
            w_str = self._move_to_algebraic(w)
            if i + 1 < len(moves):
                b = moves[i+1]
                b_str = self._move_to_algebraic(b)
                self.move_listbox.insert(tk.END, f"{i//2+1}. {w_str}  {b_str}")
            else:
                self.move_listbox.insert(tk.END, f"{i//2+1}. {w_str}")

    def _move_to_algebraic(self, move):
        if move['castle'] == 'kingside':
            return "O-O"
        if move['castle'] == 'queenside':
            return "O-O-O"
        piece = move['piece']
        ptype = piece[1]
        p_symbol = {'k': 'K', 'q': 'Q', 'r': 'R', 'b': 'B', 'n': 'N', 'p': ''}[ptype]
        from_c = move['from'][1]
        capture = move['captured'] != ''
        to_r, to_c = move['to']
        promo = move['promotion']
        disambiguation = ""
        if ptype == 'p' and capture:
            disambiguation = chr(ord('a') + from_c)
        capture_str = 'x' if capture else ''
        dest = chr(ord('a') + to_c) + str(BOARD_SIZE - to_r)
        promo_str = ('=' + promo.upper()) if promo else ''
        return disambiguation + p_symbol + capture_str + dest + promo_str

    # --- Click handler (human moves) ---
    def on_click(self, event):
        if self.startup or self.game_over or self.mode is None:
            return
        # Only handle if it's a human's turn
        if self.mode == 'human_white' and self.game.current_player != 'w':
            return
        if self.mode == 'human_black' and self.game.current_player != 'b':
            return
        # In human vs human, both are human, so always allowed

        offset = COORDINATE_SIZE
        col = (event.x - offset) // SQUARE_SIZE
        row = (event.y - offset) // SQUARE_SIZE
        if not in_bounds(row, col):
            return

        if self.game.promotion_pending:
            return

        piece = self.game.board[row][col]
        color = get_piece_color(piece)

        if self.selected is None:
            if piece != '' and color == self.game.current_player:
                self.selected = (row, col)
                self.legal_moves_for_selected = []
                moves = self.game.get_piece_moves(row, col)
                for tr, tc in moves:
                    if self.game.is_legal_move(row, col, tr, tc):
                        self.legal_moves_for_selected.append((tr, tc))
                self.draw_board()
        else:
            sr, sc = self.selected
            if (row, col) in self.legal_moves_for_selected:
                # Legal move – execute
                result = self.game.make_move(sr, sc, row, col)
                if result == 'promotion':
                    self.show_promotion_dialog(row, col)
                else:
                    self.selected = None
                    self.legal_moves_for_selected = []
                    self.draw_board()
                    self.update_move_list()
                    self.check_game_state()
                    if not self.game_over and self.should_ai_move():
                        self.root.after(500, self.do_ai_move)
            else:
                # Click on own piece -> re-select
                if piece != '' and color == self.game.current_player:
                    self.selected = (row, col)
                    self.legal_moves_for_selected = []
                    moves = self.game.get_piece_moves(row, col)
                    for tr, tc in moves:
                        if self.game.is_legal_move(row, col, tr, tc):
                            self.legal_moves_for_selected.append((tr, tc))
                    self.draw_board()
                else:
                    self.selected = None
                    self.legal_moves_for_selected = []
                    self.draw_board()

    def show_promotion_dialog(self, row, col):
        top = tk.Toplevel(self.root)
        top.title("Promotion")
        top.geometry("200x100")
        top.transient(self.root)
        top.grab_set()
        label = tk.Label(top, text="Choose promotion piece:")
        label.pack(pady=5)
        frame = tk.Frame(top)
        frame.pack()
        for choice, symbol in [('q', '♛'), ('r', '♜'), ('b', '♝'), ('n', '♞')]:
            btn = tk.Button(frame, text=symbol, font=("Arial Unicode MS", 20),
                            command=lambda ch=choice: self.promote_choice(top, row, col, ch))
            btn.pack(side=tk.LEFT, padx=5)

    def promote_choice(self, top, row, col, choice):
        self.game.promote(row, col, choice)
        top.destroy()
        self.selected = None
        self.legal_moves_for_selected = []
        self.draw_board()
        self.update_move_list()
        self.check_game_state()
        if not self.game_over and self.should_ai_move():
            self.root.after(500, self.do_ai_move)

    # --- AI move ---
    def should_ai_move(self):
        if self.game_over or self.mode is None:
            return False
        if self.mode == 'human_white' and self.game.current_player == 'b':
            return True
        if self.mode == 'human_black' and self.game.current_player == 'w':
            return True
        return False

    def do_ai_move(self):
        if self.game_over or self.startup:
            return
        if not self.should_ai_move():
            return
        self.status_var.set("AI is thinking...")
        self.root.update()

        move = self.ai.find_best_move(self.game)
        if move is None:
            self.status_var.set("AI has no move")
            self.check_game_state()
            return

        from_r, from_c = move['from']
        to_r, to_c = move['to']
        promo = move['promotion']
        result = self.game.make_move(from_r, from_c, to_r, to_c, promo if promo else None)
        if result == 'promotion':
            self.game.promote(to_r, to_c, 'q')  # AI promotes to queen
        self.selected = None
        self.legal_moves_for_selected = []
        self.draw_board()
        self.update_move_list()
        self.status_var.set("Ready")
        self.check_game_state()
        if not self.game_over and self.should_ai_move():
            # In case AI must move again (shouldn't happen)
            self.root.after(500, self.do_ai_move)

    # --- Game state ---
    def check_game_state(self):
        player = self.game.current_player
        if self.game.is_in_check(self.game.board, player):
            if not self.game.has_legal_moves(player):
                messagebox.showinfo("Game Over", f"Checkmate! {enemy_color(player).upper()} wins!")
                self.game_over = True
            else:
                messagebox.showinfo("Check", f"{player.upper()} is in check!")
        else:
            if not self.game.has_legal_moves(player):
                messagebox.showinfo("Game Over", "Stalemate!")
                self.game_over = True

    def undo_move(self):
        if self.game_over or self.startup:
            return
        if self.game.undo_last_move():
            self.selected = None
            self.legal_moves_for_selected = []
            self.draw_board()
            self.update_move_list()
            self.status_var.set("Undo")
            if not self.game_over and self.should_ai_move():
                self.root.after(500, self.do_ai_move)
        else:
            messagebox.showinfo("Undo", "Nothing to undo.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()