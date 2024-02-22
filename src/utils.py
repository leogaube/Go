class Stone:
    EMPTY = 0
    BLACK = 1
    WHITE = 2


class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BROWN = [196, 164, 132]


def get_color(stone):
    if stone == Stone.BLACK:
        return Color.BLACK
    elif stone == Stone.WHITE:
        return Color.WHITE


def get_opposite_stone(stone):
    assert stone != Stone.EMPTY
    if stone == Stone.BLACK:
        return Stone.WHITE
    return Stone.BLACK


def make_2d_array(h, w, default=lambda: None):
    return [[default() for i in range(w)] for j in range(h)]
