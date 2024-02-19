import pygame

WHITE = [255, 255, 255]
BLACK = [0, 0, 0]
BROWN = [196, 164, 132]

BOARD_SIZE = 9
SCREEN_SIZE = 800
DISTANCE = SCREEN_SIZE // (BOARD_SIZE + 1)


class UI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))

        self.c = 0
        self.color = BLACK
        self.hover_pos = None

        self.stones = [[], []]

    def change_color(self):
        if self.color == BLACK:
            self.c = 1
            self.color = WHITE
        else:
            self.c = 0
            self.color = BLACK
        self.hover_pos = None

    def _place_stone(self):
        if not self.hover_pos:
            return

        self.stones[self.c].append(self.hover_pos)
        self.change_color()

    def _draw_board(self):
        self.screen.fill(BROWN)

        for yi in range(1, 10):
            pygame.draw.line(
                self.screen,
                BLACK,
                [DISTANCE, yi * (DISTANCE)],
                [SCREEN_SIZE - DISTANCE, yi * (DISTANCE)],
                4,
            )

        for xi in range(1, 10):
            pygame.draw.line(
                self.screen,
                BLACK,
                [xi * (DISTANCE), DISTANCE],
                [xi * (DISTANCE), SCREEN_SIZE - DISTANCE],
                4,
            )

    def _draw_stones(self):
        for c, color in enumerate([BLACK, WHITE]):
            for yi, xi in self.stones[c]:
                pygame.draw.circle(
                    self.screen,
                    color,
                    ((xi + 1) * DISTANCE, (yi + 1) * DISTANCE),
                    DISTANCE * 0.35,
                )

    def _draw_hover(self):
        yi, xi = self.hover_pos
        pygame.draw.circle(
            self.screen,
            self.color,
            ((xi + 1) * DISTANCE, (yi + 1) * DISTANCE),
            DISTANCE * 0.35,
        )
        pygame.draw.circle(
            self.screen,
            "gray",
            ((xi + 1) * DISTANCE, (yi + 1) * DISTANCE),
            DISTANCE * 0.35,
            5,
        )

    def _move_hover(self, y_offset=0, x_offset=0):
        if not self.hover_pos:
            self.hover_pos = [BOARD_SIZE // 2, BOARD_SIZE // 2]
        else:
            assert y_offset or x_offset
            self.hover_pos[0] += y_offset
            self.hover_pos[1] += x_offset

            # skip over already placed stones
            while self.hover_pos in self.stones[0] + self.stones[1]:
                self.hover_pos[0] += y_offset
                self.hover_pos[1] += x_offset

            for i in [0, 1]:
                if self.hover_pos[i] < 0:
                    self.hover_pos[i] = BOARD_SIZE - 1
                elif self.hover_pos[i] > BOARD_SIZE - 1:
                    self.hover_pos[i] = 0

    def handle_user_input(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return -1

                elif event.key == pygame.K_UP:
                    self._move_hover(y_offset=-1)
                elif event.key == pygame.K_DOWN:
                    self._move_hover(y_offset=1)
                elif event.key == pygame.K_LEFT:
                    self._move_hover(x_offset=-1)
                elif event.key == pygame.K_RIGHT:
                    self._move_hover(x_offset=1)

                elif event.key == pygame.K_RETURN:
                    if self.hover_pos:
                        self._place_stone()

        self._draw_board()
        self._draw_stones()
        if self.hover_pos:
            self._draw_hover()

        pygame.display.flip()


if __name__ == "__main__":
    ui = UI()

    clock = pygame.time.Clock()

    while ui.handle_user_input() != -1:
        clock.tick(30)
