"""a game of tic tac toe (that you can't win)"""

import pyglet
from pyglet.window import mouse
from board import Board

window = pyglet.window.Window()
board = Board(window)


@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        board.set_last_quad(x, y)


@window.event
def on_mouse_release(x, y, button, modifiers):
    if button == mouse.LEFT:
        if board.player_plays(x, y):
            board.computer_plays()


@window.event
def on_draw():
    board.draw()


pyglet.app.run()
