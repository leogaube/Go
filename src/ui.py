import pygame

WHITE = [255, 255, 255]
BLACK = [0, 0, 0]
BROWN = [196, 164, 132]

BOARD_SIZE = 9
SCREEN_SIZE = 800
DISTANCE = SCREEN_SIZE // (BOARD_SIZE + 1)
STONE_RADIUS = DISTANCE * 0.4

assert BOARD_SIZE % 2 == 1


def out_off_bounds(pos):
    y, x = pos
    if y < 0 or x < 0 or y >= BOARD_SIZE or x >= BOARD_SIZE:
        return True
    return False


def get_surrounding_positions(center, offset):
    """returns all positions that sourround the center with a given offset."""
    y, x = center
    for y_offset in range(-offset, offset + 1):
        for x_offset in range(offset, -offset - 1, -1):
            if abs(y_offset) + abs(x_offset) != offset:
                continue
            pos = [y + y_offset, x + x_offset]
            if out_off_bounds(pos):
                continue
            yield pos


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

    def _pass_move(self):
        self.change_color()

    def _draw_board(self):
        self.screen.fill(BROWN)

        for yi in range(1, BOARD_SIZE + 1):
            pygame.draw.line(
                self.screen,
                BLACK,
                [DISTANCE, yi * (DISTANCE)],
                [SCREEN_SIZE - DISTANCE, yi * (DISTANCE)],
                4,
            )

        for xi in range(1, BOARD_SIZE + 1):
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
                    STONE_RADIUS,
                )

    def _draw_hover(self):
        yi, xi = self.hover_pos
        pygame.draw.circle(
            self.screen,
            self.color,
            ((xi + 1) * DISTANCE, (yi + 1) * DISTANCE),
            STONE_RADIUS * 0.8,
        )
        # pygame.draw.circle(
        #     self.screen,
        #     "gray",
        #     ((xi + 1) * DISTANCE, (yi + 1) * DISTANCE),
        #     STONE_RADIUS,
        #     5,
        # )

    def _move_hover(self, y_offset=0, x_offset=0):
        if not self.hover_pos:
            self._default_hover()
            return

        def skip_stones():
            # skip over already placed stones
            while self.hover_pos in self.stones[0] + self.stones[1]:
                self.hover_pos[0] += y_offset
                self.hover_pos[1] += x_offset

        def skip_edges():
            # move to the opposite side of the board
            for i in [0, 1]:
                if self.hover_pos[i] < 0:
                    self.hover_pos[i] = BOARD_SIZE - 1
                    skip_stones()
                elif self.hover_pos[i] > BOARD_SIZE - 1:
                    self.hover_pos[i] = 0
                    skip_stones()

        assert y_offset or x_offset
        self.hover_pos[0] += y_offset
        self.hover_pos[1] += x_offset

        skip_stones()
        skip_edges()

    def _default_hover(self):
        center = [BOARD_SIZE // 2, BOARD_SIZE // 2]
        for ring_size in range(BOARD_SIZE):
            for y, x in get_surrounding_positions(center, ring_size):
                if [y, x] not in self.stones[0] + self.stones[1]:
                    self.hover_pos = [y, x]
                    return
        # raise BoardFullException

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

                elif event.key == pygame.K_p:
                    self._pass_move()

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
