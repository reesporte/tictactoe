from random import choice
import pyglet
from pyglet import shapes


class Board:
    def __init__(self, window):
        self.window = window
        self.last_quad = None
        self.board = {
            q: None
            for q in [
                (0, 0),
                (1, 0),
                (2, 0),
                (0, 1),
                (1, 1),
                (2, 1),
                (0, 2),
                (1, 2),
                (2, 2),
            ]
        }

        self.block_height = self.window.height // 3
        self.block_width = self.window.width // 3

        self.player_quads = []
        self.cpu_quads = []

        self.game_over = False

        self.win_sets = {}
        self._init_win_sets()

    def _init_win_sets(self):
        """setup a mapping of quadrants to potential wins in that quadrant"""
        for win_set in [
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)],
        ]:
            for quad in win_set:
                if self.win_sets.get(quad, False):
                    self.win_sets[quad].append(win_set)
                else:
                    self.win_sets[quad] = [win_set]

    def _draw_shape(self, shape, quadrant):
        """draws a shape"""
        if shape == "x":
            self.board[quadrant] = shapes.Star(
                (quadrant[0] * self.block_width) + (self.block_width // 2),
                (quadrant[1] * self.block_height) + (self.block_height // 2),
                self.window.width // 12,
                10,
                4,
                45,
            )
        elif shape == "o":
            self.board[quadrant] = shapes.Circle(
                (quadrant[0] * self.block_width) + (self.block_width // 2),
                (quadrant[1] * self.block_height) + (self.block_height // 2),
                self.window.width // 12,
            )

    def _draw_lines(self):
        """draw the board lines"""
        # horizontal
        for i in range(1, 3):
            pyglet.graphics.draw(
                2,
                pyglet.gl.GL_LINES,
                (
                    "v2i",
                    (
                        i,
                        i * self.block_height,
                        self.window.width,
                        i * self.block_height,
                    ),
                ),
            )
        # vertical
        for i in range(1, 3):
            pyglet.graphics.draw(
                2,
                pyglet.gl.GL_LINES,
                (
                    "v2i",
                    (
                        self.block_width * i,
                        i,
                        self.block_width * i,
                        self.window.height,
                    ),
                ),
            )

    def draw(self):
        """draw the board"""
        self.window.clear()
        self._draw_lines()
        for shape in self.board.values():
            if shape:
                shape.draw()
        if self.game_over:
            pyglet.text.Label(
                "you didnt win!",
                font_size=36,
                x=self.window.width // 2,
                y=self.window.height // 2,
                anchor_x="center",
                anchor_y="center",
                color=(201, 58, 22, 255),
            ).draw()

    def _get_quad(self, x, y):
        """convert coordinates to a quadrant on the board"""
        return ((x // (self.window.width // 3)), (y // (self.window.height // 3)))

    def set_last_quad(self, x, y):
        """sets the last quad the player touched"""
        self.last_quad = self._get_quad(x, y)

    def _available_quad(self, x, y):
        """can you put a piece on this quadrant"""
        q = self._get_quad(x, y)
        return (not self.board.get(q, False)) and q == self.last_quad

    def _available_quads(self):
        """return a list of all quadrants without a shape"""
        return [quad for quad, shape in self.board.items() if not shape]

    def player_plays(self, x, y):
        """returns whether the player has made a valid move"""
        if not self.game_over:
            if self._available_quad(x, y):
                self.player_quads.append(self._draw_shape("x", self._get_quad(x, y)))
                return True
        return False

    def is_win(self, quad, who, board):
        """does `who` win if it plays this quad"""
        check = ""
        if who == "cpu":
            check = "<class 'pyglet.shapes.Circle'>"
        elif who == "player":
            check = "<class 'pyglet.shapes.Star'>"

        for win_set in self.win_sets[quad]:
            tile_count = 0
            for position in win_set:
                if str(type(board.get(position, ""))) == check:
                    tile_count += 1
            if tile_count == 2 and not board[quad]:
                return True
        return False

    def is_fork(self, quad, who, board):
        """can `who` fork using this quad on this board"""
        check = ""
        if who == "cpu":
            check = "<class 'pyglet.shapes.Circle'>"
        elif who == "player":
            check = "<class 'pyglet.shapes.Star'>"
        fork_sets = 0
        for win_set in self.win_sets[quad]:
            blank_tiles = 3
            player_tiles = 0
            for position in win_set:
                if str(type(board.get(position, ""))) == check:
                    player_tiles += 1
                if board.get(position, False):
                    blank_tiles -= 1
            if blank_tiles == 2 and player_tiles == 1:
                fork_sets += 1
            if fork_sets == 2:
                return True
        return fork_sets == 2

    def count_wins(self, quad, who, board):
        """count the number of different ways `who` could win on this quad"""
        check = ""
        if who == "cpu":
            check = "<class 'pyglet.shapes.Circle'>"
        elif who == "player":
            check = "<class 'pyglet.shapes.Star'>"
        wins = 0
        for win_set in self.win_sets[quad]:
            tile_count = 0
            for position in win_set:
                if str(type(board.get(position, ""))) == check:
                    tile_count += 1
            if tile_count == 2 and not self.board[quad]:
                wins += 1
        return wins

    def available_center(self):
        """is the center empty?"""
        return self.board.get((1, 1)) is None

    def opposite_corner(self):
        """if there is a player in a corner, return the opposite corner"""
        quad = None
        for position in [(0, 0), (0, 2), (2, 2), (2, 0)]:
            if str(type(self.board.get(position))) == "<class 'pyglet.shapes.Star'>":
                quad = position

        if quad is None:
            return None

        retval = [0, 0]
        if quad[0] == 2:
            retval[0] = 0
        else:
            retval[0] = 2
        if quad[1] == 2:
            retval[1] = 0
        else:
            retval[1] = 2
        if self.board.get(tuple(retval)):
            return None
        return tuple(retval)

    def empty_corner(self):
        """if there is an empty corner, return it"""
        for position in [(0, 0), (0, 2), (2, 2), (2, 0)]:
            if self.board.get(position) is None:
                return position
        return None

    def cpu_block_forks(self, forks):
        """get the spot that blocks all forks"""
        if len(forks) == 1:
            return forks[0]

        quad_to_forks = {}
        for quad in self._available_quads():
            # make a hypothetical board
            board = {quad: val for quad, val in self.board.items()}
            board[quad] = shapes.Circle(0, 0, 0)

            # we start by assuming it is a fork
            isfork = 0
            for f in forks:
                # check if it's still a fork on our hypothetical board
                fork = self.is_fork(f, "player", board)
                if fork:
                    # if it is, check if we can block it with a potential win
                    # get all the other quads that we haven't used yet
                    quads = [q for q in self._available_quads() if q != quad]
                    for q in quads:
                        # in each of those, check if we can win next turn if we fill in that quad
                        board_copy = {q: v for q, v in board.items()}
                        board_copy[q] = shapes.Circle(0, 0, 0)
                        for next_quadrant in [qu for qu in quads if qu != q]:
                            if (
                                self.is_win(next_quadrant, "cpu", board)
                                and next_quadrant != f
                            ):
                                fork = False
                                break
                isfork += fork
            quad_to_forks[quad] = isfork

        minimum = 99999
        minquad = None
        for quad, forks in quad_to_forks.items():
            if forks == 0:
                return quad
            elif forks < minimum:
                minimum = forks
                minquad = quad
        return minquad

    def computer_plays(self):
        """have the computer play the best it can"""
        quads = self._available_quads()
        if len(quads) < 1:
            # if there are no more places to go, game is over
            self.game_over = True
            return

        blocks = []
        forks = []
        for quad in quads:
            if self.is_win(quad, "cpu", self.board):
                self.game_over = True
                return self._draw_shape("o", quad)

            if self.is_win(quad, "player", self.board):
                blocks.append(quad)

            if self.is_fork(quad, "player", self.board):
                forks.append(quad)

            if self.is_fork(quad, "cpu", self.board):
                return self._draw_shape("o", quad)

        if len(blocks) > 0:
            return self._draw_shape("o", choice(blocks))

        if len(forks) > 0:
            return self._draw_shape("o", self.cpu_block_forks(forks))

        if self.available_center():
            return self._draw_shape("o", (1, 1))

        opposite_corner = self.opposite_corner()
        if opposite_corner:
            return self._draw_shape("o", opposite_corner)

        empty_corner = self.empty_corner()
        if empty_corner:
            return self._draw_shape("o", empty_corner)

        self._draw_shape("o", choice(quads))
