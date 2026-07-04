# chess_engine.py
# Core chess logic – no GUI, no AI

BOARD_SIZE = 8

# Unicode piece symbols (for reference only, not used in engine)
PIECE_SYMBOLS = {
    'wp': '♙', 'wn': '♘', 'wb': '♗', 'wr': '♖', 'wq': '♕', 'wk': '♔',
    'bp': '♟', 'bn': '♞', 'bb': '♝', 'br': '♜', 'bq': '♛', 'bk': '♚'
}

INITIAL_BOARD = [
    ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
    ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
    ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
]

# --- Helpers ---
def in_bounds(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

def get_piece_color(piece):
    return None if piece == '' else piece[0]

def enemy_color(color):
    return 'b' if color == 'w' else 'w'

def copy_board(board):
    return [row[:] for row in board]

def square_name(r, c):
    return chr(ord('a') + c) + str(BOARD_SIZE - r)


class ChessGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = copy_board(INITIAL_BOARD)
        self.current_player = 'w'
        self.castle_rights = {
            'w': {'king': True, 'queen': True},
            'b': {'king': True, 'queen': True}
        }
        self.en_passant_target = None
        self.move_history = []
        self.history_snapshots = []   # for undo
        self.promotion_pending = None

    # --- Move Generation (pseudo-legal) ---

    def get_piece_moves(self, r, c, board=None, castle_rights=None, en_passant_target=None):
        if board is None:
            board = self.board
        if castle_rights is None:
            castle_rights = self.castle_rights
        if en_passant_target is None:
            en_passant_target = self.en_passant_target

        piece = board[r][c]
        if piece == '':
            return []
        color = get_piece_color(piece)
        ptype = piece[1]

        if ptype == 'p':
            return self._pawn_moves(board, r, c, color, en_passant_target)
        elif ptype == 'n':
            return self._knight_moves(board, r, c, color)
        elif ptype == 'b':
            return self._bishop_moves(board, r, c, color)
        elif ptype == 'r':
            return self._rook_moves(board, r, c, color)
        elif ptype == 'q':
            return self._queen_moves(board, r, c, color)
        elif ptype == 'k':
            return self._king_moves(board, r, c, color, castle_rights)
        return []

    def _pawn_moves(self, board, r, c, color, en_passant_target):
        moves = []
        direction = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1

        # Forward one
        nr, nc = r + direction, c
        if in_bounds(nr, nc) and board[nr][nc] == '':
            moves.append((nr, nc))
            # Forward two from starting row
            nr2 = r + 2 * direction
            if r == start_row and board[nr2][nc] == '':
                moves.append((nr2, nc))

        # Captures
        for dc in (-1, 1):
            nr, nc = r + direction, c + dc
            if in_bounds(nr, nc):
                target = board[nr][nc]
                if target != '' and get_piece_color(target) != color:
                    moves.append((nr, nc))
                # En passant
                if en_passant_target and (nr, nc) == en_passant_target:
                    if (color == 'w' and r == 3) or (color == 'b' and r == 4):
                        moves.append((nr, nc))
        return moves

    def _knight_moves(self, board, r, c, color):
        moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in offsets:
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc):
                target = board[nr][nc]
                if target == '' or get_piece_color(target) != color:
                    moves.append((nr, nc))
        return moves

    def _bishop_moves(self, board, r, c, color):
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            for step in range(1, BOARD_SIZE):
                nr, nc = r + step * dr, c + step * dc
                if not in_bounds(nr, nc):
                    break
                target = board[nr][nc]
                if target == '':
                    moves.append((nr, nc))
                else:
                    if get_piece_color(target) != color:
                        moves.append((nr, nc))
                    break
        return moves

    def _rook_moves(self, board, r, c, color):
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            for step in range(1, BOARD_SIZE):
                nr, nc = r + step * dr, c + step * dc
                if not in_bounds(nr, nc):
                    break
                target = board[nr][nc]
                if target == '':
                    moves.append((nr, nc))
                else:
                    if get_piece_color(target) != color:
                        moves.append((nr, nc))
                    break
        return moves

    def _queen_moves(self, board, r, c, color):
        return self._bishop_moves(board, r, c, color) + self._rook_moves(board, r, c, color)

    def _king_moves(self, board, r, c, color, castle_rights):
        moves = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc):
                    target = board[nr][nc]
                    if target == '' or get_piece_color(target) != color:
                        moves.append((nr, nc))

        # Castling
        if (color == 'w' and (r, c) == (7, 4)) or (color == 'b' and (r, c) == (0, 4)):
            if castle_rights[color]['king']:
                if (color == 'w' and board[7][5] == '' and board[7][6] == '' and board[7][7] == 'wr') or \
                   (color == 'b' and board[0][5] == '' and board[0][6] == '' and board[0][7] == 'br'):
                    moves.append((r, c + 2))
            if castle_rights[color]['queen']:
                if (color == 'w' and board[7][1] == '' and board[7][2] == '' and board[7][3] == '' and board[7][0] == 'wr') or \
                   (color == 'b' and board[0][1] == '' and board[0][2] == '' and board[0][3] == '' and board[0][0] == 'br'):
                    moves.append((r, c - 2))
        return moves

    # --- Check and Legality ---

    def find_king(self, board, color):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] == color + 'k':
                    return (r, c)
        return None

    def is_in_check(self, board, color, castle_rights=None, en_passant_target=None):
        king_pos = self.find_king(board, color)
        if not king_pos:
            return True
        kr, kc = king_pos
        enemy = enemy_color(color)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = board[r][c]
                if piece != '' and get_piece_color(piece) == enemy:
                    moves = self.get_piece_moves(r, c, board, castle_rights, en_passant_target)
                    if (kr, kc) in moves:
                        return True
        return False

    def is_legal_move(self, from_r, from_c, to_r, to_c):
        piece = self.board[from_r][from_c]
        if piece == '' or get_piece_color(piece) != self.current_player:
            return False
        moves = self.get_piece_moves(from_r, from_c)
        if (to_r, to_c) not in moves:
            return False

        # Simulate the move on a copy
        board_copy = copy_board(self.board)
        castle_copy = {col: self.castle_rights[col].copy() for col in ('w', 'b')}
        ep_copy = self.en_passant_target
        self._apply_move(board_copy, from_r, from_c, to_r, to_c, castle_copy, ep_copy)

        # Check if own king is in check
        if self.is_in_check(board_copy, self.current_player, castle_copy, ep_copy):
            return False
        return True

    def _apply_move(self, board, from_r, from_c, to_r, to_c, castle_rights, en_passant_target):
        piece = board[from_r][from_c]
        color = get_piece_color(piece)
        ptype = piece[1]

        # En passant capture
        if ptype == 'p' and en_passant_target and (to_r, to_c) == en_passant_target:
            board[from_r][to_c] = ''

        # Move piece
        board[to_r][to_c] = piece
        board[from_r][from_c] = ''

        # Castling rook movement
        if ptype == 'k':
            if to_c - from_c == 2:  # kingside
                if color == 'w':
                    board[7][5] = 'wr'
                    board[7][7] = ''
                else:
                    board[0][5] = 'br'
                    board[0][7] = ''
            elif to_c - from_c == -2:  # queenside
                if color == 'w':
                    board[7][3] = 'wr'
                    board[7][0] = ''
                else:
                    board[0][3] = 'br'
                    board[0][0] = ''

        # Update castling rights
        if ptype == 'k':
            castle_rights[color]['king'] = False
            castle_rights[color]['queen'] = False
        elif ptype == 'r':
            if color == 'w':
                if from_r == 7 and from_c == 0:
                    castle_rights['w']['queen'] = False
                elif from_r == 7 and from_c == 7:
                    castle_rights['w']['king'] = False
            else:
                if from_r == 0 and from_c == 0:
                    castle_rights['b']['queen'] = False
                elif from_r == 0 and from_c == 7:
                    castle_rights['b']['king'] = False

    # --- Make Move (with promotion handling) ---

    def make_move(self, from_r, from_c, to_r, to_c, promotion_choice=None):
        if not self.is_legal_move(from_r, from_c, to_r, to_c):
            return False

        # Save state for undo
        self.history_snapshots.append((
            copy_board(self.board),
            {col: self.castle_rights[col].copy() for col in ('w', 'b')},
            self.en_passant_target,
            self.current_player
        ))

        piece = self.board[from_r][from_c]
        color = get_piece_color(piece)
        ptype = piece[1]

        # Store captured piece (before moving)
        captured = self.board[to_r][to_c]
        ep_capture = False
        if ptype == 'p' and self.en_passant_target and (to_r, to_c) == self.en_passant_target:
            ep_capture = True
            captured = self.board[from_r][to_c]

        # Apply the move
        self._apply_move(self.board, from_r, from_c, to_r, to_c, self.castle_rights, self.en_passant_target)

        # If a rook was captured, update opponent's rights
        if captured:
            capt_color = get_piece_color(captured)
            if capt_color and captured[1] == 'r':
                if capt_color == 'w':
                    if to_r == 7 and to_c == 0:
                        self.castle_rights['w']['queen'] = False
                    elif to_r == 7 and to_c == 7:
                        self.castle_rights['w']['king'] = False
                else:
                    if to_r == 0 and to_c == 0:
                        self.castle_rights['b']['queen'] = False
                    elif to_r == 0 and to_c == 7:
                        self.castle_rights['b']['king'] = False

        # Determine castle type for notation
        castle_type = None
        if ptype == 'k':
            if to_c - from_c == 2:
                castle_type = 'kingside'
            elif to_c - from_c == -2:
                castle_type = 'queenside'

        # Pawn promotion
        promotion = None
        if ptype == 'p' and (to_r == 0 or to_r == 7):
            if promotion_choice is None:
                self.promotion_pending = (to_r, to_c, color)
                return 'promotion'
            else:
                self.board[to_r][to_c] = color + promotion_choice
                promotion = promotion_choice

        # Set en passant target
        if ptype == 'p' and abs(to_r - from_r) == 2:
            self.en_passant_target = ((from_r + to_r) // 2, from_c)
        else:
            self.en_passant_target = None

        # Record move
        move_info = {
            'from': (from_r, from_c),
            'to': (to_r, to_c),
            'piece': piece,
            'captured': captured,
            'castle': castle_type,
            'promotion': promotion,
            'ep': ep_capture
        }
        self.move_history.append(move_info)

        # Switch turns
        self.current_player = enemy_color(color)
        return True

    def promote(self, to_r, to_c, choice):
        color = get_piece_color(self.board[to_r][to_c])
        self.board[to_r][to_c] = color + choice
        self.promotion_pending = None
        self.current_player = enemy_color(color)

    def undo_last_move(self):
        if not self.history_snapshots:
            return False
        self.board, self.castle_rights, self.en_passant_target, self.current_player = self.history_snapshots.pop()
        self.move_history.pop()
        self.promotion_pending = None
        return True

    # --- Utilities ---

    def has_legal_moves(self, color):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.board[r][c]
                if piece != '' and get_piece_color(piece) == color:
                    moves = self.get_piece_moves(r, c)
                    for tr, tc in moves:
                        old = self.current_player
                        self.current_player = color
                        if self.is_legal_move(r, c, tr, tc):
                            self.current_player = old
                            return True
                        self.current_player = old
        return False

    def get_all_legal_moves(self, color):
        """Return a list of moves as dicts with 'from', 'to', 'promotion'."""
        moves = []
        old_player = self.current_player
        self.current_player = color
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.board[r][c]
                if piece != '' and get_piece_color(piece) == color:
                    pseudo = self.get_piece_moves(r, c)
                    for tr, tc in pseudo:
                        if self.is_legal_move(r, c, tr, tc):
                            ptype = piece[1]
                            if ptype == 'p' and (tr == 0 or tr == 7):
                                # For AI, we add four promotion options
                                for promo in ['q', 'r', 'b', 'n']:
                                    moves.append({'from': (r, c), 'to': (tr, tc), 'promotion': promo})
                            else:
                                moves.append({'from': (r, c), 'to': (tr, tc), 'promotion': None})
        self.current_player = old_player
        return moves