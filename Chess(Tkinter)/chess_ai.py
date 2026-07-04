# chess_ai.py
# AI opponent with iterative deepening, move ordering, and time control

import time
from chess_engine import BOARD_SIZE, ChessGame, copy_board, enemy_color, get_piece_color

class ChessAI:
    def __init__(self, depth=3, time_limit=2.0):
        self.max_depth = depth          # fallback if time runs out
        self.time_limit = time_limit    # seconds per move
        self.piece_values = {
            'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000
        }

        # Piece-square tables (middlegame, white's perspective)
        self.pawn_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5,  5, 10, 25, 25, 10,  5,  5],
            [0,  0,  0, 20, 20,  0,  0,  0],
            [5, -5,-10,  0,  0,-10, -5,  5],
            [5, 10, 10,-20,-20, 10, 10,  5],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ]
        self.knight_table = [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ]
        self.bishop_table = [
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10, 10, 10, 10, 10, 10, 10,-10],
            [-10,  5,  0,  0,  0,  0,  5,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20]
        ]
        self.rook_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [5, 10, 10, 10, 10, 10, 10,  5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [0,  0,  0,  5,  5,  0,  0,  0]
        ]
        self.queen_table = [
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [-5,  0,  5,  5,  5,  5,  0, -5],
            [0,  0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20]
        ]
        self.king_table = [
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
            [20, 20,  0,  0,  0,  0, 20, 20],
            [20, 30, 10,  0,  0, 10, 30, 20]
        ]
        self.tables = {
            'p': self.pawn_table,
            'n': self.knight_table,
            'b': self.bishop_table,
            'r': self.rook_table,
            'q': self.queen_table,
            'k': self.king_table
        }

    def evaluate(self, board, color):
        """Evaluate board from 'color's perspective (positive = good for color)."""
        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = board[r][c]
                if piece == '':
                    continue
                pcolor = get_piece_color(piece)
                ptype = piece[1]
                val = self.piece_values[ptype]
                table = self.tables[ptype]
                if pcolor == 'w':
                    pos_score = table[r][c]
                else:
                    pos_score = table[BOARD_SIZE-1-r][c]  # mirror for black
                if pcolor == color:
                    score += val + pos_score
                else:
                    score -= val + pos_score
        return score

    def order_moves(self, moves, board):
        """Sort moves: captures first, then by piece value of captured piece."""
        def move_score(move):
            to_r, to_c = move['to']
            target = board[to_r][to_c]
            if target:
                attacker = board[move['from'][0]][move['from'][1]]
                # MVV-LVA: Most Valuable Victim - Least Valuable Attacker
                return 10 * self.piece_values[target[1]] - self.piece_values[attacker[1]]
            return 0
        moves.sort(key=move_score, reverse=True)
        return moves

    def minimax(self, board, depth, alpha, beta, maximizing, game_state,
                castle_rights, en_passant, current_player):
        if depth == 0:
            return self.evaluate(board, game_state.current_player), None

        # Generate legal moves
        temp_game = game_state.__class__()   # create a fresh game to avoid modifying original
        temp_game.board = copy_board(board)
        temp_game.castle_rights = {col: castle_rights[col].copy() for col in ('w', 'b')}
        temp_game.en_passant_target = en_passant
        temp_game.current_player = current_player

        moves = temp_game.get_all_legal_moves(current_player)
        if not moves:
            if temp_game.is_in_check(board, current_player, castle_rights, en_passant):
                return -100000 + (self.max_depth - depth), None  # checkmate
            else:
                return 0, None  # stalemate

        # Move ordering
        self.order_moves(moves, board)

        best_move = None
        if maximizing:
            max_eval = -float('inf')
            for move in moves:
                # Simulate move
                board_copy = copy_board(board)
                castle_copy = {col: castle_rights[col].copy() for col in ('w', 'b')}
                ep_copy = en_passant
                new_board, new_castle, new_ep, new_player = self._simulate_move(
                    board_copy, castle_copy, ep_copy, current_player, move
                )
                eval, _ = self.minimax(new_board, depth-1, -beta, -alpha, False,
                                       game_state, new_castle, new_ep, enemy_color(current_player))
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if alpha >= beta:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                board_copy = copy_board(board)
                castle_copy = {col: castle_rights[col].copy() for col in ('w', 'b')}
                ep_copy = en_passant
                new_board, new_castle, new_ep, new_player = self._simulate_move(
                    board_copy, castle_copy, ep_copy, current_player, move
                )
                eval, _ = self.minimax(new_board, depth-1, alpha, beta, True,
                                       game_state, new_castle, new_ep, enemy_color(current_player))
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def _simulate_move(self, board, castle_rights, en_passant, player, move):
        """Apply a move dict to a board copy and return new state."""
        from_r, from_c = move['from']
        to_r, to_c = move['to']
        promo = move['promotion']

        temp = ChessGame()   # we only need its _apply_move
        temp.board = board
        temp.castle_rights = castle_rights
        temp.en_passant_target = en_passant
        temp.current_player = player

        temp._apply_move(board, from_r, from_c, to_r, to_c, castle_rights, en_passant)

        # Handle promotion
        if promo:
            piece = board[to_r][to_c]
            color = get_piece_color(piece)
            board[to_r][to_c] = color + promo

        # Update en passant target (after pawn double push)
        piece = board[to_r][to_c]
        if piece and piece[1] == 'p' and abs(to_r - from_r) == 2:
            en_passant = ((from_r + to_r)//2, from_c)
        else:
            en_passant = None

        new_player = enemy_color(player)
        return board, castle_rights, en_passant, new_player

    def find_best_move(self, game_state):
        """Iterative deepening with time limit."""
        start = time.time()
        best_move = None
        # Try increasing depths until time runs out
        for depth in range(1, self.max_depth + 1):
            if time.time() - start > self.time_limit:
                break
            _, move = self.minimax(game_state.board, depth, -float('inf'), float('inf'),
                                   True, game_state,
                                   game_state.castle_rights,
                                   game_state.en_passant_target,
                                   game_state.current_player)
            if move:
                best_move = move
        return best_move