import pygame
from itertools import product

from helperClass.constants import WHITE, GRAY, P1_COLOR, P2_COLOR, HOLE_COLOR, SQUARE_SIZE, SQUARE_PAD, ROWS, COLS
from helperClass.pieces import Piece, PlayerPiece, HolePiece
from helperClass.scoreMaker import ScoreMarker


class Board:
    def __init__(self, first_player):

        self.selected_piece = None
        self.target_square = None

        self.last_move = [(-1, -1)]

        self.turn = P1_COLOR if first_player == 0 else P2_COLOR

        self.p1_score = 0
        self.p2_score = 0

        self.square = pygame.Rect(0, 0, SQUARE_SIZE - SQUARE_PAD, SQUARE_SIZE - SQUARE_PAD)
        self.board = [[None] * COLS for j in range(ROWS)]

        self.p1_pieces = []
        self.p2_pieces = []

        for col in range(1, COLS - 1):
            self.board[ROWS - 2][col] = PlayerPiece(P1_COLOR, ROWS - 2, col)  # pieces in 5th row
            self.board[1][col] = PlayerPiece(P2_COLOR, 1, col)  # pieces in 1st row

            self.p1_pieces.append(self.board[ROWS - 2][col])
            self.p2_pieces.append(self.board[1][col])

        self.board[3][3] = HolePiece(HOLE_COLOR, 3, 3)
        self.hole_piece = self.board[3][3]

        # Markers for scoring
        self.score_markers = []
        self.score_markers.append(ScoreMarker(P1_COLOR, 1))
        self.score_markers.append(ScoreMarker(P1_COLOR, 2))
        self.score_markers.append(ScoreMarker(P2_COLOR, 4))
        self.score_markers.append(ScoreMarker(P2_COLOR, 5))

    def __str__(self):
        color_dict = {None: "0", P1_COLOR: "1", P2_COLOR: "2", HOLE_COLOR: "X"}
        return "\n".join(["".join([color_dict[piece.color] if piece else "0" for piece in row]) for row in self.board])

    def save_state(self, affected_spaces):

        modified_spaces = tuple([tuple([row, col, self.board[row][col]]) for row, col in affected_spaces])
        return self.turn, self.p1_score, self.p2_score, self.last_move[:], modified_spaces

    def restore_state(self, state):

        self.turn, self.p1_score, self.p2_score, self.last_move, modified_spaces = state
        for row, col, piece in modified_spaces:
            self.board[row][col] = piece
            if piece is not None:
                piece.move(row, col)

    def set_selected(self, pos) -> None:

        self.board[pos[0]][pos[1]].toggle_selected()
        if pos == self.selected_piece:
            print("Deselected piece:", pos)
            self.selected_piece = None
            return

        self.selected_piece = pos
        print("Selected piece:", pos)

    def set_target_square(self, pos) -> None:

        if pos is None:
            self.target_square = None
            print("Deselected target square:", pos)

        self.target_square = pos
        print("Selected square:", pos)

    def get_piece(self, pos):
        return self.board[pos[0]][pos[1]]

    def draw_grid(self, win):

        win.fill(GRAY)
        for row, col in product(range(1, ROWS - 1), range(1, COLS - 1)):
            self.square.center = ((SQUARE_SIZE // 2) + row * SQUARE_SIZE, (SQUARE_SIZE // 2) + col * SQUARE_SIZE)
            pygame.draw.rect(win, WHITE, self.square)

    def toggle_selected(self, pos):

        self.board[pos[0]][pos[1]].toggle_selected()

    def draw_pieces(self, win):

        for row in range(ROWS):
            for col in range(COLS):
                if self.board[row][col] is not None:
                    self.board[row][col].draw(win)

    def draw_score(self, win):

        for piece in self.score_markers:
            piece.draw(win)

    @staticmethod
    def is_out_of_bounds(row, col) -> bool:

        return row < 1 or row > ROWS - 2 or col < 1 or col > COLS - 2

    def is_turn(self, piece):
        # return: True if piece belongs to current player or is the Hole, False if opposite player's color
        return piece.color == self.turn or piece.color == HOLE_COLOR

    def get_turn_player(self):
        return self.turn

    def try_move(self, current_row: int, current_col: int, target_row: int, target_col: int, pieces_moved=None):

        if pieces_moved is None:
            pieces_moved = []

        # Check for invalid move - cannot push Hole off of board or onto another piece
        if self.board[current_row][current_col].get_color() == HOLE_COLOR and (
                self.is_out_of_bounds(target_row, target_col) or self.board[target_row][target_col] is not None):
            return None

        # Move may be good. Add to list of pieces moved this time and test further
        pieces_moved.append((current_row, current_col))

        # Pushing a piece off the board or into the hole eliminates it, so there's no way this move is duplicating the
        # last board state. Move successful.
        if self.is_out_of_bounds(target_row, target_col) or self.board[target_row][target_col] is not None and \
                self.board[target_row][target_col].color == HOLE_COLOR:
            pieces_moved.append((target_row, target_col))
            return pieces_moved

        # Pushing a piece into another piece requires recursion
        if self.board[target_row][target_col] is not None:
            ph_row, ph_col = target_row, target_col
            target_row, target_col = 2 * target_row - current_row, 2 * target_col - current_col
            current_row, current_col = ph_row, ph_col
            return self.try_move(current_row, current_col, target_row, target_col, pieces_moved)

        # Pushing onto an empty square is valid, but we have to check if we are simply reversing the last move made,
        # and returning to the preceding board position which is invalid.
        pieces_moved.append((target_row, target_col))
        if pieces_moved == list(reversed(self.last_move)):
            return None

        return pieces_moved

    def is_adjacent(self, current_row: int, current_col: int, target_row: int, target_col: int):

        row_delta = abs(current_row - target_row)
        col_delta = abs(current_col - target_col)

        return (row_delta == 0 and col_delta == 1) or (row_delta == 1 and col_delta == 0)

    def drop_piece(self, piece: Piece) -> None:

        piece.move(-1, -1)
        if piece.get_color() == P2_COLOR:
            self.p1_score += 1
        else:
            self.p2_score += 1

    def get_winner(self):
        if self.p1_score == 2:
            return P1_COLOR

        if self.p2_score == 2:
            return P2_COLOR

        return None

    def update_score_markers(self):

        if self.p1_score == 1:
            self.score_markers[2].activate()
        if self.p1_score == 2:
            self.score_markers[3].activate()
        if self.p2_score == 1:
            self.score_markers[0].activate()
        if self.p2_score == 2:
            self.score_markers[1].activate()

    def move_pieces(self, move_list: list((int, int))) -> None:

        target_row, target_col = move_list.pop()
        while move_list:
            if self.is_out_of_bounds(target_row, target_col) or self.board[target_row][target_col] is not None and \
                    self.board[target_row][target_col].color == HOLE_COLOR:
                self.drop_piece(self.board[move_list[-1][0]][move_list[-1][1]])
                self.board[move_list[-1][0]][move_list[-1][1]] = None
                # Dropping a piece means the next move cannot be a reverse of the current one
                # We reset last_move to avoid edge case where dropping a piece into the hole makes it so the
                # hole can't be moved
                self.last_move = [(-1, -1)]
            else:
                self.board[move_list[-1][0]][move_list[-1][1]].move(target_row, target_col)
                self.board[target_row][target_col] = self.board[move_list[-1][0]][move_list[-1][1]]
                self.board[move_list[-1][0]][move_list[-1][1]] = None

            if move_list:
                target_row, target_col = move_list.pop()

    def take_turn(self, current_row: int, current_col: int, target_row: int, target_col: int, hypothetical=False):

        self.selected_piece and self.set_selected(self.selected_piece)

        print(f"Attempting turn {current_row},{current_col} to {target_row},{target_col}")

        if not self.is_adjacent(current_row, current_col, target_row, target_col):
            print("Squares are not adjacent")
            return False

        moved = self.try_move(current_row, current_col, target_row, target_col)
        if not moved:
            return False

        # This will be a valid move. Now actually move the pieces, record as the last move, and change turn player
        self.last_move = moved[:]
        self.move_pieces(moved)

        # Update score markers if this is real move and not AI projection
        hypothetical or self.update_score_markers()

        self.turn = P2_COLOR if self.turn == P1_COLOR else P1_COLOR

        return True
