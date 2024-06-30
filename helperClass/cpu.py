import copy
import random

from helperClass.constants import P1_COLOR, P2_COLOR


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
        # print("possible move:")
        # print(move_candidates)
        if maxplayer:
            for start_row, start_col, target_row, target_col in move_candidates:

                move = self.board.try_move(start_row, start_col, target_row, target_col)
                # print("move_cpu: ", move)
                if move:
                    state = self.board.save_state(move)
                    # print("state_cpu:", state)
                    if self.board.take_turn(start_row, start_col, target_row, target_col, True):
                        if not best_move:
                            best_move = (start_row, start_col, target_row, target_col)
                        score, _ = self.minmax(depth - 1, not maxplayer, alpha, beta)

                        # print("score_cpu: ", score)
                        self.board.restore_state(state)
                        # print("max: ", current_max)
                        if score > current_max:
                            current_max = score
                            best_move = (start_row, start_col, target_row, target_col)
                            alpha = max(score, alpha)
                            if score >= beta:
                                break
            # print("curr_max_final", current_max)
            # print("best_move", best_move)
            return current_max, best_move


        else:
            for start_row, start_col, target_row, target_col in move_candidates:
                move = self.board.try_move(start_row, start_col, target_row, target_col)
                # print("move_human")
                if move:
                    state = self.board.save_state(move)
                    # print("state_human")
                    if self.board.take_turn(start_row, start_col, target_row, target_col, True):
                        score, _ = self.minmax(depth - 1, not maxplayer, alpha, beta)
                        # print("score_human: ", score)
                        self.board.restore_state(state)
                        # print("cur_min: ", current_min)
                        if score < current_min:
                            current_min = score
                            beta = min(score, beta)
                            if score <= alpha:
                                break
            # print("cur_min: ", current_min)
            return current_min, None

    def initializePopulation(self):

        population_state = []
        for i in range(2):
            if i == 0:
                pieces = self.board.p2_pieces
                turn = "p2"
            else:
                turn = "p1"
                pieces = self.board.p1_pieces

            move_candidates = []

            pieces = pieces + [self.board.hole_piece]
            for piece in pieces:
                if piece.row == -1:
                    continue
                for neighbor in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    row, col = piece.row + neighbor[0], piece.col + neighbor[1]
                    if not (self.board.is_out_of_bounds(row, col) or self.board.board[row][
                        col] == self.board.hole_piece):
                        move_candidates.append((piece.row, piece.col, row, col))

            for start_row, start_col, target_row, target_col in move_candidates:
                move = self.board.try_move(start_row, start_col, target_row, target_col)
                data = []
                if move:
                    state = self.board.save_state(move)
                    if self.board.take_turn(start_row, start_col, target_row, target_col, True):
                        # print("after turn:")
                        # self.initializePopulation(depth-1)

                        print(start_row, start_col, target_row, target_col, turn)
                        data.append([start_row, start_col, target_row, target_col, turn])
                        self.copy_board = copy.deepcopy(self.board)
                        data.append(self.copy_board)
                        population_state.append(data)
                        self.board.restore_state(state)

        return population_state

    def fitness(self, brd):
        if brd.p2_score == 2:
            return 100

        if brd.p1_score == 2:
            return -100

        score = 0
        if brd.p1_score == 1:
            score -= 10

        if brd.p2_score == 1:
            score += 10

        for piece in brd.p1_pieces:
            # print("row col p1")
            # print(piece.row, piece.col)
            score -= self.calculate_piece_score(piece)
            # print("score row col p1")
            # print(score)

        for piece in brd.p2_pieces:
            # print("row col p2")
            # print(piece.row, piece.col)
            score += self.calculate_piece_score(piece)
            # print("score row col p2")
            # print(score)

        # Being next to the Hole is an added vulnerability
        for neighbor in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            row, col = brd.hole_piece.row + neighbor[0], brd.hole_piece.col + neighbor[1]
            if brd.board[row][col] and brd.board[row][col].color == P1_COLOR:
                score += 1
            if brd.board[row][col] and brd.board[row][col].color == P2_COLOR:
                score -= 1

        return score

    def selection(self, population):
        # score_list = []
        selected = []
        p2_scorelist = []
        p1_scorelist = []
        p2_population = []
        p1_population = []
        for data in population:
            # print(data[0])
            score = self.fitness(data[1])
            if data[0][4] == "p2":
                p2_population.append(data)
                p2_scorelist.append(score)
            else:
                p1_scorelist.append(score)
                p1_population.append(data)
            # score_list.append(score)

        p1_ln = len(p1_population)
        p2_ln = len(p2_population)

        # print("p1_popu: ", p1_ln)
        # print(p1_population)
        # print("p2_popu: ", p2_ln)
        # print(p2_population)

        for i in range(2):

            if i == 0:
                ln = p2_ln
                popu = p2_population
                score_list = p2_scorelist
            else:
                ln = p1_ln
                popu = p1_population
                score_list = p1_scorelist

            already_selected = []
            mid = ln // 2
            cnt = 0
            while cnt != mid:
                selected_index = random.sample(range(ln), 2)
                if selected_index in already_selected:
                    continue

                already_selected.append(selected_index)
                selected_board = [popu[ind] for ind in selected_index]
                selected_fitness = [score_list[ind] for ind in selected_index]

                if i == 0:
                    best_fitness_index = selected_fitness.index(max(selected_fitness))
                else:
                    best_fitness_index = selected_fitness.index(min(selected_fitness))

                best_chromosome = selected_board[best_fitness_index]

                if best_chromosome in selected:
                    continue

                selected.append(best_chromosome)
                cnt += 1

        return selected

    def crossover(self, parent1, parent2):

        move = parent1[0]
        brd = parent2[1]

        data = []
        data.append(move)

        mv = brd.try_move(move[0], move[1], move[2], move[3])
        if mv:
            state = brd.save_state(mv)
            if brd.take_turn(move[0], move[1], move[2], move[3], True):
                data.append(copy.deepcopy(brd))
                brd.restore_state(state)
                return data

        return None

    def genetic(self):
        population = self.initializePopulation()

        # print("board test")
        # print(len(population))
        # print("populations")
        # print(population)

        selected_poulation = self.selection(population)
        print("selected population: ", len(selected_poulation))
        print(selected_poulation)

        p2 = []
        p1 = []

        for data in selected_poulation:
            if data[0][4] == "p2":
                p2.append(data)
            else:
                p1.append(data)

        offspring = []
        for x in p2:
            for y in p1:
                move = x[0]
                bd = y[1]
                if bd.board[move[0]][move[1]] is None:
                    continue
                offspring.append(self.crossover(x, y))

        print("offspring: ", len(offspring))
        # print(offspring)

        # for data in offspring:
        #     if data is not None:
        #         array = [['_' for _ in range(5)] for _ in range(5)]
        #         print(data[0])
        #         for p in data[1].p2_pieces:
        #             if p.row == -1:
        #                 continue
        #             array[p.row - 1][p.col - 1] = '#'
        #         for p in data[1].p1_pieces:
        #             if p.row == -1:
        #                 continue
        #             array[p.row - 1][p.col - 1] = '*'
        #         h = data[1].hole_piece
        #         array[h.row - 1][h.col - 1] = 'O'
        #         print(array)

        scores = []
        for child in offspring:
            if child is not None:
                scores.append((child[0], self.fitness(child[1])))

        print("offspring score: ", len(scores))
        print(scores)
        max_tuple = max(scores, key=lambda item: item[1])
        print(max_tuple)

        # best_index = scores.index(max(scores))
        # print("score child: ", scores[best_index])
        # print("best move: ", offspring[best_index])

        # data = offspring[best_index]
        move = max_tuple[0]
        best_move = (move[0], move[1], move[2], move[3])

        return max_tuple[1], best_move

    def find_move(self, difficulty):
        if difficulty == 5:
            from_gen = self.genetic()
            print(from_gen)
            # ga = GeneticAlgorithm(self.board)
            # return ga.find_move()
            return from_gen

        perfect = self.minmax(difficulty, True)
        # print("cnt: ", self.cnt)
        print("perfect:")
        print(perfect)
        return perfect
