#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import copy
import numpy as np
import time
from .evaluate_functions import *
import math
import random



# to do Diego
# update legal moves function
# update result function
# Finish entire pipeline
# remove bugs (I didn't test anything sorry)
#
class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def _init_(self):
        super()._init_()

    def compute_best_move(self, game_state: GameState) -> None:
        """ 
        Proposes the best playable move found using minimax within the timespan given by the game settings."""

        


    
    

# Assuming the existence of the Node class and related functions as per the previous pseudo code

def monte_carlo_tree_search(root, max_iterations=1000):
    for _ in range(max_iterations):
        node = traverse(root) #chatgpt
        best_child = best_uct(node) #chatgpt
        simulation_result = rollout(best_child) #chatpgpt
        backpropagate(best_child, simulation_result) #chatgpt

    return best_child(root)

def traverse(node):
    while not is_terminal(node) and is_fully_expanded(node):
        legal_moves_list = legal_moves(node.state) # chat
        for move in legal_moves_list:              # chat
            child_state = apply_move(node, move)   # chat
            if node.turn_player:                   # Turn player functionality added by Diego
                child_node = create_node(child_state, parent=node, move=move, False) #chat
                node.children.append(child_node) # chat
            else:
                child_node = create_node(child_state, parent=node, move=move, True) # chat
                node.children.append(child_node) #chat
    return pick_unvisited(node.children) or node #chat


def rollout(node): #chat
    while not is_terminal(node):
        node = rollout_policy(node)
    return result(node)

def rollout_policy(node): #chat, but turn player Diego
    legal_moves_list = legal_moves(node.state) #chat
    random_move = random.choice(legal_moves_list)
    next_state = apply_move(node, random_move)  # Implement apply_move based on your game #I should track scores?
    if node.turn_player: #Diego
        return create_node(next_state, parent=node, turn_player=False)
    else:
        return create_node(next_state, parent=node, turn_player=True)
        
def backpropagate(node, result): #chat
    while node is not None:
        node = update_stats(node, result)
        node = node.parent #this looks strange
        

def best_uct(node): #chat
    # Select the child with the highest UCB value
    exploration_constant = 1.414  # Adjust as needed
    children_with_ucb = [(child, ucb_value(node, child, exploration_constant)) for child in node.children]
    best_child = max(children_with_ucb, key=lambda x: x[1])[0]
    return best_child

def ucb_value(parent, child, exploration_constant): #chat
    exploitation_term = child.total_reward / child.visit_count if child.visit_count != 0 else 0
    exploration_term = math.sqrt(math.log(parent.visit_count) / child.visit_count) if child.visit_count != 0 else 0
    return exploitation_term + exploration_constant * exploration_term

def result(node): #to do chat,
    # Return the result of the simulation for the given node's state
    # should be a 1 for win or a 0 for loss, i think
    # we can do this score-based
    pass
    # to do



# Example usage:
# initial_state = initialize_game_state()
# root = create_node(initial_state)
# best_move = monte_carlo_tree_search(root).state
    

    
    
class Node:
    def __init__(self, state):
        self.state = state #chat
        self.children = [] #chat # List to store child nodes
        self.parent = None #chat  # Parent node
        self.visit_count = 0 #chat
        self.total_reward = 0.0 #chat
        self.move = None #chat #move played to get to certain node
        self.scores = scores #Diego
        self.turn_player = turn_player #Diego

def create_node(state, parent=None, move=None, scores=None, turn_player=None):
    node = Node(state)
    node.parent = parent
    node.move = move #chat
    node.scores = scores #Diego
    node.turn_player = turn_player #Diego
    return node

def is_fully_expanded(node): #chat
    # Check if all possible actions from this state have corresponding child nodes
    return len(node.children) == len(legal_moves(node.state))

def is_terminal(node):
    # Check if the game state is terminal
    #deze code, is sus
    empty_indices = [index for index, value in enumerate(board.squares) if value == 0] #chat

    if len(empty_indices) != 0:
        return False #diego
    
    return True #Diego
    #return game_over(node.state)

def legal_moves(state):
    #to do
    pass

# Example utility function
def apply_move(node, move): #Diego
    state_copy = copy.deepcopy(node.state)
    points = get_points(state_copy, move)
    state_copy.board.put(move[0], move[1], 1)
    if node.turn_player:
        state_copy.scores = [state_copy.scores[0] + points, state_copy.scores[1]]
    else:
        state_copy.scores = [state_copy.scores[0], state_copy.scores[1] + points]
    
    return state_copy

def game_over(state): #chat, I think pass
    # Check if the game is over for the given state
    # I can pass this for now, since I don't have a sudoku solver.
    pass

def pick_unvisited(children): #chat
    # Return an unvisited child node if any, else return None
    for child in children:
        if child.visit_count == 0:
            return child
    return None

def update_stats(node, result): #chat
    # Update the visit count and total reward based on the result of a simulation
    node.visit_count += 1
    node.total_reward += result
    return node

