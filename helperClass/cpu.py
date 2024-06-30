import copy
import random

from packages.constants import P1_COLOR, P2_COLOR
from packages.genetic import GeneticAlgorithm
from test import GeneticTest


class Automa:
    def __init__(self, board):
        self.copy_board = None
        self.board = board
        self.genetic_move = []
        self.cnt = 0

    @staticmethod
    def calculate_piece_score(piece) -> int:
        # Central squares are worth 2, 1 less for each side on edge of board (making corner squares 0)

        if piece.row == -1:
            return 0
        curr_score = 2
        if piece.row == 1 or piece.row == 5:
            curr_score -= 1
        if piece.col == 1 or piece.col == 5:
            curr_score -= 1
        return curr_score

    def calculate_score(self, depth) -> float | int:
        """
        Calculates the score based on board position and remaining pieces
        :return: Total score. Positive if p1 has advantage, negative if p2 does
        """
        # Victories outweigh other possible scores, but earlier victories are better
        if self.board.p2_score == 2:
            return 100 + depth

        if self.board.p1_score == 2:
            return -100 - depth

        score = 0

        if self.board.p1_score == 1:
            score -= 10

        if self.board.p2_score == 1:
            score += 10

        for piece in self.board.p1_pieces:
            print("row col p1")
            print(piece.row, piece.col)
            score -= self.calculate_piece_score(piece)
            print("score row col p1")
            print(score)

        for piece in self.board.p2_pieces:
            score += self.calculate_piece_score(piece)

        # Being next to the Hole is an added vulnerability
        for neighbor in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            row, col = self.board.hole_piece.row + neighbor[0], self.board.hole_piece.col + neighbor[1]
            if self.board.board[row][col] and self.board.board[row][col].color == P1_COLOR:
                score += 1
            if self.board.board[row][col] and self.board.board[row][col].color == P2_COLOR:
                score -= 1

        return score

    def minmax(self, depth: int, maxplayer: bool, alpha: float = float("-inf"), beta: float = float("inf")):
        if depth == 0 or self.board.p1_score == 2 or self.board.p2_score == 2:
            return self.calculate_score(depth), None

        self.cnt += 1
        best_move = None
        current_max = float("-inf")
        current_min = float("inf")
        move_candidates = []

        if maxplayer:
            pieces = self.board.p2_pieces
            print("cpu assumption")
        else:
            pieces = self.board.p1_pieces
            print("human assumption")
        pieces = pieces + [self.board.hole_piece]

        for piece in pieces:

            print(piece.row, piece.col)

            if piece.row == -1:
                continue
            for neighbor in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                row, col = piece.row + neighbor[0], piece.col + neighbor[1]
                if not (self.board.is_out_of_bounds(row, col) or self.board.board[row][col] == self.board.hole_piece):
                    move_candidates.append((piece.row, piece.col, row, col))
        print("possible move:")
        print(move_candidates)
        if maxplayer:
            for start_row, start_col, target_row, target_col in move_candidates:

                move = self.board.try_move(start_row, start_col, target_row, target_col)
                print("move_cpu: ", move)
                if move:
                    state = self.board.save_state(move)
                    print("state_cpu:", state)
                    if self.board.take_turn(start_row, start_col, target_row, target_col, True):
                        if not best_move:
                            best_move = (start_row, start_col, target_row, target_col)
                        score, _ = self.minmax(depth - 1, not maxplayer, alpha, beta)

                        print("score_cpu: ", score)
                        self.board.restore_state(state)
                        print("max: ", current_max)
                        if score > current_max:
                            current_max = score
                            best_move = (start_row, start_col, target_row, target_col)
                            alpha = max(score, alpha)
                            if score >= beta:
                                break
            print("curr_max_final", current_max)
            print("best_move", best_move)
            return current_max, best_move


        else:
            for start_row, start_col, target_row, target_col in move_candidates:
                move = self.board.try_move(start_row, start_col, target_row, target_col)
                print("move_human")
                if move:
                    state = self.board.save_state(move)
                    print("state_human")
                    if self.board.take_turn(start_row, start_col, target_row, target_col, True):
                        score, _ = self.minmax(depth - 1, not maxplayer, alpha, beta)
                        print("score_human: ", score)
                        self.board.restore_state(state)
                        print("cur_min: ", current_min)
                        if score < current_min:
                            current_min = score
                            beta = min(score, beta)
                            if score <= alpha:
                                break
            print("cur_min: ", current_min)
            return current_min, None



    def find_move(self, difficulty):

        perfect = self.minmax(difficulty, True)
        # print("cnt: ", self.cnt)
        print("perfect:")
        print(perfect)
        return perfect
