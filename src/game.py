from src.board import Board
from src.utils import *
from src.group import Group, GroupManager
from src.ui import UI
from src.exceptions import (
    SelfDestructException,
    KoException,
    InvalidInputException,
    BoardFullException,
)

import pygame


class Game(object):
    """
    Manage the high level gameplay of Go
    """

    def __init__(self, config):

        # 2D board
        self.board = Board(config)

        # dimension of the square board
        self.board_size = config["board_size"]

        # group manager instance
        self.gm = GroupManager(
            self.board, enable_self_destruct=config["enable_self_destruct"]
        )

        # count the number of consecutive passes
        self.count_pass = 0

    def place_black(self, y, x):
        """
        Place a black stone at coordinate (y, x)
        """
        self._place_stone(Stone.BLACK, y, x)

    def place_white(self, y, x):
        """
        Place a white stone at coordinate (y, x)
        """
        self._place_stone(Stone.WHITE, y, x)

    def pass_turn(self):
        """
        Pass this turn
        """
        self.count_pass += 1

    def is_over(self):
        """
        Check if the game is over (only if there are two consecutive passes)
        """
        return self.count_pass >= 2

    def is_within_bounds(self, y, x):
        """
        Check if the given coordinate is within the range of the board
        """
        return self.board.is_within_bounds(y, x)

    def _place_stone(self, stone, y, x):
        """
        Place a stone at (y, x), then resolve interactions due to the move.
        Throw an exception if self-destruct or ko rules are violated
        """
        if stone == Stone.EMPTY:
            return
        self.board.place_stone(stone, y, x)

        try:
            self.gm.resolve_board(y, x)
        except SelfDestructException as e:
            self.board.remove_stone(y, x)
            raise e
        except KoException as e:
            self.board.remove_stone(y, x)
            raise e

        self.count_pass = 0
        self.gm.update_state()

    @property
    def num_black_captured(self):
        """
        Return the number of captured black stones
        """
        return self.gm._num_captured_stones[Stone.BLACK]

    @property
    def num_white_captured(self):
        """
        Return the number of captured white stones
        """
        return self.gm._num_captured_stones[Stone.WHITE]

    def render_board(self):
        """
        Render the board
        """
        self.board._render()

    def get_scores(self):
        """
        Return the score of black and white.
        Scoring is counted based on territorial rules, with no interpolation of dead/alive groups.
        An area is a territory for a player if any area within that territory can only reach
        stones of of that player.
        """
        scores = {Stone.BLACK: 0, Stone.WHITE: 0}
        traversed = make_2d_array(
            self.board_size, self.board_size, default=lambda: False
        )

        def traverse(y, x):
            traversed[y][x] = True
            search = [(y, x)]
            stone = None
            count = 1
            is_neutral = False

            while search:
                y, x = search.pop()
                for ly, lx in self.board.get_liberty_coords(y, x):
                    this_stone = self.board[ly, lx]
                    if this_stone != Stone.EMPTY:
                        stone = stone or this_stone
                        if stone != this_stone:
                            is_neutral = True
                    if not traversed[ly][lx]:
                        if this_stone == Stone.EMPTY:
                            count += 1
                            search.append((ly, lx))
                    traversed[ly][lx] = True

            if is_neutral:
                return 0, Stone.EMPTY
            return count, stone

        for y in range(self.board_size):
            for x in range(self.board_size):
                if not traversed[y][x] and self.board[y, x] == Stone.EMPTY:
                    score, stone = traverse(y, x)
                    if stone is not None and stone != Stone.EMPTY:
                        scores[stone] += score

        scores[Stone.BLACK] -= self.num_black_captured
        scores[Stone.WHITE] -= self.num_white_captured
        return scores


class GameUI(object):
    """
    Main interface between the game and the players
    """

    def __init__(self, config):

        # the game object
        self.game = Game(config)

        # the pygame user interface
        self.ui = UI(config)

        # store which player's turn it is
        self.turn = Stone.BLACK
        self.hover_pos = None

        self.board_size = config["board_size"]

        self.ui.render(self.game.board, self.turn, self.hover_pos)

    def play(self):
        """
        Start the game of Go. Two players alternate turns placing stones on the board
        until the game is over.
        """

        while not self.game.is_over():
            is_turn_over = False
            self.game.render_board()

            while not is_turn_over:
                move = self.handle_user_input()
                if move is None:
                    continue
                elif move == "pass":
                    self.game.pass_turn()
                    is_turn_over = True
                else:
                    is_turn_over = self._place_stone(move)

            self.ui.render(self.game.board, self.turn, self.hover_pos)
            self._switch_turns()

        self._display_result()

    def _move_hover(self, y_offset=0, x_offset=0):
        if not self.hover_pos:
            self._default_hover()
            return

        def skip_stones():
            # skip over already placed stones
            y, x = self.hover_pos
            while self.game.board[y][x] != Stone.EMPTY:
                self.hover_pos[0] += y_offset
                self.hover_pos[1] += x_offset
                if self.out_off_bounds(self.hover_pos):
                    skip_edges()
                elif self.hover_pos == org_pos:
                    self.hover_pos = self.next_best_position(org_pos)
                y, x = self.hover_pos

        def skip_edges():
            # move to the opposite side of the board
            for i in [0, 1]:
                if self.hover_pos[i] < 0:
                    self.hover_pos[i] = self.board_size - 1
                    skip_stones()
                elif self.hover_pos[i] > self.board_size - 1:
                    self.hover_pos[i] = 0
                    skip_stones()

        org_pos = list(self.hover_pos)

        assert y_offset or x_offset
        self.hover_pos[0] += y_offset
        self.hover_pos[1] += x_offset

        if not self.out_off_bounds(self.hover_pos):
            skip_stones()
        skip_edges()

        self.ui.render(self.game.board, self.turn, self.hover_pos)

    def _default_hover(self):
        center = [self.board_size // 2, self.board_size // 2]
        self.hover_pos = self.next_best_position(center)
        self.ui.render(self.game.board, self.turn, self.hover_pos)

    def next_best_position(self, center):
        for ring_size in range(self.board_size):
            for y, x in self.get_surrounding_positions(center, ring_size):
                if self.game.board[y][x] == Stone.EMPTY:
                    return [y, x]
        raise BoardFullException

    def out_off_bounds(self, pos):
        y, x = pos
        if y < 0 or x < 0 or y >= self.board_size or x >= self.board_size:
            return True
        return False

    def get_surrounding_positions(self, center, offset):
        """returns all positions that sourround the center with a given offset."""
        y, x = center
        for y_offset in range(-offset, offset + 1):
            for x_offset in range(offset, -offset - 1, -1):
                if abs(y_offset) + abs(x_offset) != offset:
                    continue
                pos = [y + y_offset, x + x_offset]
                if self.out_off_bounds(pos):
                    continue
                yield pos

    def handle_user_input(self):
        move = None
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
                        move = self.hover_pos

                elif event.key == pygame.K_p:
                    move = "pass"

        return move

    def _display_result(self):
        """
        Show the result of the game including the scores and winner
        """
        scores = self.game.get_scores()
        black_score = scores[Stone.BLACK]
        white_score = scores[Stone.WHITE]

        print(f"Black score: {black_score}")
        print(f"White score: {white_score}")

        if black_score == white_score:
            print("The result is a tie!")
        else:
            winner = Stone.BLACK if black_score > white_score else Stone.WHITE
            winner = self._get_player_name(winner)
            print(f"The winner is {winner}!")

    def _place_stone(self, move):
        """
        Place a stone at the specified coordinate. Return True if it is valid
        """
        y, x = move
        try:
            if self.turn == Stone.BLACK:
                self.game.place_black(y, x)
            elif self.turn == Stone.WHITE:
                self.game.place_white(y, x)
            is_turn_over = True
        except Exception as e:
            print(e)
            is_turn_over = False
        return is_turn_over

    def _get_player_name(self, stone):
        """
        Return the player name for the specified stone
        """
        return "Black" if stone == Stone.BLACK else "White"

    def _switch_turns(self):
        """
        Swap the turn
        """
        self.turn = Stone.BLACK if self.turn == Stone.WHITE else Stone.WHITE

    def _prompt_move(self):
        """
        Prompt a user input move. The input format is one of
            - "pass" to pass for the current player   or
            - "y x" to place a stone at the specified coordinate
        The prompt repeats until a valid input is given
        """
        move = None
        player = self._get_player_name(self.turn)
        while not self._is_valid_input(move):
            print(
                "Please input a valid move"
                '(enter "pass" to pass or "y x" to place a stone at the coordinate (y, x))'
            )
            move = input(f"{player} move: ")

        return self._parse_move(move)

    def _is_valid_input(self, move):
        """
        Check if the given input would give a valid move, in terms of placing a stone
        on the board
        """
        if move == "pass":
            return True
        try:
            y, x = self._parse_coordinates(move)
            return self.game.is_within_bounds(y, x)
        except:
            return False

    def _parse_coordinates(self, move):
        """
        Parse the coordinate input into (y, x) valid coordinates
        """
        y, x = move.strip().split()
        y = self._label_to_coord(y)
        x = self._label_to_coord(x)
        return y, x

    def _label_to_coord(self, label):
        """
        Translate an individual input coordinate into a valid one.
        The labels are given as 0, 1, 2, ... , 9, A, B, ...
        This helper translates all labels into integer coordinates
        Eg. _label_to_coord('9') --> 9
            _label_to_coord('A') --> 10
            _label_to_coord('C') --> 12
        """
        if label.isnumeric():
            coord = int(label)
            if coord >= 10:
                raise InvalidInputException
            return int(label)
        if label.isalpha() and label >= "A":
            diff = ord(label) - ord("A")
            if diff < 0:
                raise InvalidInputException
            return 10 + diff
        raise InvalidInputException

    def _parse_move(self, move):
        """
        Parse an arbitrary input
        """
        if move == "pass":
            return move
        return self._parse_coordinates(move)
