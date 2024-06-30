from ctypes import Union

import pygame
import pygame_menu
from helperClass.constants import WIDTH, HEIGHT, SQUARE_SIZE, P1_COLOR, P2_COLOR
from helperClass.playground import Board
from random import randint
from helperClass.cpu import Automa
from helperClass.messages import showMessage
from pygame_menu import sound


class Game:

    def __init__(self):
        pygame.init()
        self.WIN = pygame.display.set_mode((WIDTH, HEIGHT))
        self.FPS = 60
        pygame.display.set_caption("KnockOut!")
        self.difficulty = 2

    def getMode(self):
        return self.mode

    def setMode(self, mode):
        self.mode: Union[str, pygame_menu.Menu, None] = mode

    def get_start_new_game(self):
        return self.start_new_game

    def set_start_new_game(self, newgame):
        self.start_new_game = newgame

    @staticmethod
    def get_row_col(pos: (int, int)) -> (int, int):

        return pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE

    def set_difficulty(self, difficulty_str: str, difficulty_num: int) -> None:
        self.difficulty = difficulty_num
        print(f"Difficulty {self.difficulty}")

    def run_game(self):

        while True:
            # We have to re-run game setup when we start a new game
            self.mode = "main_menu"
            self.start_new_game = False

            # randomly determine starting player
            first_player = randint(0, 1)

            run = True
            clock = pygame.time.Clock()
            board = Board(first_player)
            automa = Automa(board)

            main_menu = pygame_menu.Menu('KnockOut', WIDTH / 2, HEIGHT / 2, theme=pygame_menu.themes.THEME_SOLARIZED)
            main_menu.add.button('Play', self.setMode, "announce_first")
            main_menu.add.selector('Difficulty: ', [("Easy", 2), ("Medium", 3), ("Hard", 4), ("Guest", 5)],
                                   onchange=self.set_difficulty)
            main_menu.add.button('Quit', pygame_menu.events.EXIT)

            engine = sound.Sound()
            engine.set_sound(sound.SOUND_TYPE_CLICK_MOUSE, 'assets/click.ogx')

            main_menu.set_sound(engine, recursive=True)
            self.setMode(main_menu)

            while run and not self.start_new_game:
                clock.tick(self.FPS)

                if board.get_winner():
                    self.mode = "winner"

                if board.get_turn_player() == P2_COLOR and self.mode == "play":

                    _, move = automa.find_move(self.difficulty)
                    print("a move")
                    print(move)
                    moving_piece = board.get_piece((move[0], move[1]))
                    print("moving: ",moving_piece.row,moving_piece.col)
                    moving_piece.toggle_selected()
                    moving_piece.draw(self.WIN)
                    pygame.display.update()
                    pygame.time.wait(1000)
                    moving_piece.toggle_selected()
                    moving_piece.draw(self.WIN)
                    pygame.display.update()
                    board.take_turn(*move, False)

                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN and self.mode == "play" and board.get_turn_player() == P1_COLOR:
                        position = self.get_row_col(pygame.mouse.get_pos())

                        selected = board.get_piece(position)
                        if board.selected_piece is None and selected is not None and board.is_turn(selected):
                            board.set_selected(position)
                        elif board.selected_piece is not None and board.selected_piece == position:
                            board.set_selected(position)
                        elif board.selected_piece is not None:
                            board.take_turn(board.selected_piece[0], board.selected_piece[1], position[0], position[1])

                if self.mode == "announce_first":
                    board.draw_grid(self.WIN)
                    board.draw_pieces(self.WIN)
                    pygame.display.update()
                    message = "You go first" if board.get_turn_player() == P1_COLOR else "CPU goes first"
                    showMessage(message, self.WIN)
                    while self.mode == "announce_first":
                        events = pygame.event.get()
                        for event in events:
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                self.mode = "play"

                if self.mode == "winner":
                    winner_message = ("You" if board.get_winner() == P1_COLOR else "CPU") + " Won!"
                    showMessage(winner_message, self.WIN)
                    while self.mode == "winner":
                        events = pygame.event.get()
                        for event in events:
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                pygame.event.wait(pygame.MOUSEBUTTONUP)
                                pygame.time.wait(250)
                                pygame.event.clear()
                                self.start_new_game = True
                                self.mode = None

                board.draw_grid(self.WIN)
                board.draw_pieces(self.WIN)
                board.draw_score(self.WIN)

                if self.mode == main_menu:
                    self.mode.draw(self.WIN)
                    self.mode.update(events)

                pygame.display.update()
