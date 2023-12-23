from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import numpy as np
import copy
from .evaluate_functions_Diego_changed import *

class Node:
    def __init__(self, state):
        self.state = state
        self.children = []  # List to store child nodes
        self.parent = None   # Parent node
        self.visit_count = 0
        self.total_reward = 0.0
        self.move = None  # move played to get to certain node
        # self.scores = state.scores
        self.turn_player = None
        self.is_root = False

def create_root(state):
    pass


def create_child_node(node, move):
    state_copy = copy.deepcopy(node.state)
    child = Node(state_copy)
    child.parent = node
    child.move = move
    points = get_points(child.state, move)
    if node.turn_player:  # player 1 to play
        node.state.scores = [node.state.scores[0] + points + node.state.scores[1]]
        child.turn_player = False  # child becomes player 2
    else:
        node.state.scores = [node.state.scores[0] + points + node.state.scores[1]]
        child.turn_player = True
    child.state.board.put(move[0], move[1], 1)  # play move on child_board

    return child






# def create_node(state, parent=None, move=None, scores=None, turn_player=None):
#     node = Node(state)
#     node.parent = parent
# #     node.move = move
# #     node.scores = scores
#     node.turn_player = turn_player
#     return node
