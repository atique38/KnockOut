from .constants import WIDTH, HEIGHT, SQUARE_SIZE, COLS, GRAY
import pygame

SCALE = .25


class ScoreMarker:
    def __init__(self, color, num):
        self.color = color
        self.curr_color = GRAY
        self.edge_length = SQUARE_SIZE * SCALE
        self.x = num * (WIDTH // COLS) + ((WIDTH // COLS - self.edge_length) // 2)
        self.y = ((HEIGHT // COLS) - self.edge_length) // 2


    def activate(self):
        self.curr_color = self.color

    def draw(self, win):
        pygame.draw.rect(win, self.curr_color, (self.x, self.y, self.edge_length, self.edge_length))
