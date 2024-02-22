from src.utils import *

import pygame


class UI:
    def __init__(self, config):
        self.board_size = config["board_size"]
        self.screen_size = config["screen_size"]

        self.cell_size = self.screen_size // (self.board_size + 1)
        self.stone_radius = self.cell_size * 0.4

        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_size, self.screen_size))

    def _draw_board(self):
        self.screen.fill(Color.BROWN)

        for yi in range(1, self.board_size + 1):
            pygame.draw.line(
                self.screen,
                Color.BLACK,
                [self.cell_size, yi * (self.cell_size)],
                [self.screen_size - self.cell_size, yi * (self.cell_size)],
                4,
            )

        for xi in range(1, self.board_size + 1):
            pygame.draw.line(
                self.screen,
                Color.BLACK,
                [xi * (self.cell_size), self.cell_size],
                [xi * (self.cell_size), self.screen_size - self.cell_size],
                4,
            )

    def _draw_stones(self, board):
        for yi in range(self.board_size):
            for xi in range(self.board_size):
                stone = board[yi][xi]
                if stone == Stone.EMPTY:
                    continue
                color = get_color(stone)
                pygame.draw.circle(
                    self.screen,
                    color,
                    ((xi + 1) * self.cell_size, (yi + 1) * self.cell_size),
                    self.stone_radius,
                )

    def _draw_hover(self, turn, hover_pos):
        yi, xi = hover_pos
        color = get_color(turn)
        pygame.draw.circle(
            self.screen,
            color,
            ((xi + 1) * self.cell_size, (yi + 1) * self.cell_size),
            self.stone_radius * 0.8,
        )

    def render(self, board, turn, hover_pos):
        self._draw_board()
        self._draw_stones(board)
        if hover_pos:
            self._draw_hover(turn, hover_pos)

        pygame.display.flip()
