#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import copy
import numpy as np
import time
from .evaluate_functions_Diego_changed import *
from .Node_class import *
import math
import random


#done
#node traverse


#optimazations
# add numpy functionlality
#call legal moves less often
# expand with not 1 node but more.

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def _init_(self):
        super()._init_()

    def compute_best_move(self, game_state: GameState) -> None:
        """ 
        Proposes the best playable move found using minimax within the timespan given by the game settings."""
        t1= time.time()
        depth = 12
        print('the depth is:', depth)
        one_state = self.only_1s_game_state(game_state)
        print(one_state)
        result = self.min_max(one_state, True, depth)
        t2 = time.time()
        print('run_time is:', t2-t1)

        root = create_node() # to fix
        monte_carlo_tree_search(root)
    
    def only_1s_game_state(self, game_state):
        '''changes all values in the sudoku board to ones'''
        one_state = copy.deepcopy(game_state)
        N = one_state.board.N
        for val1 in range(N):
            for val2 in range(N):
                #get
                val3 = one_state.board.get(val1, val2)
                if val3 != 0:
                    #overide with 1
                    one_state.board.put(val1, val2, 1)

        return one_state



# main function for the Monte Carlo Tree Search
def monte_carlo_tree_search(root, player_id):
    while resources_left(time, computational power):
        leaf = traverse(root) # use uctb to find most interrest note
        expanded_leaf = expand(leaf)                 # expand tree, in this minimal version we expand by 1 node
        simulation_result = rollout(expanded_leaf, player_id) # playout a game
        backpropagate(expanded_leaf, simulation_result) # update value's
        #add propose move functionality
        best_child = best_child(root)
        #add solve sudoku, later only do it x iterations
        #move = solve_suduku(best_child)
        #propose move
    return best_child(root) # selects best child

################## function for node traversal
def traverse(node):
    while fully_expanded(node):
        node = best_uct(node)
        node.visit_count += 1 # thus we visit this node
    # in case no children are present / node is terminal
    return node # pick_unvisited(node.children) or,
    # in case you come to a taboo _sudoku, we don't need this for only's.

def fully_expanded(node):
    # False, if no more childeren, while there are still legal moves
    return len(node.children) == len(legal_moves(node.state))

def legal_moves(state):
    # Returns all legal moves, in a list, in this case only a positions
    legal_moves_list = []
    n = state.board.N
    for i in range(n):
        for j in range(n):
            value = state.board.get(i, j)
            if value == 0:
                legal_moves_list.append([i, j])
    return legal_moves_list

def best_uct(node):
    # Select the child with the highest UCB value
    exploration_constant = 1.414  # Adjust as needed
    children_with_ucb = [(child, ucb_value(node, child, exploration_constant)) for child in node.children]
    best_child = max(children_with_ucb, key=lambda x: x[1])[0]
    #
    return best_child

def ucb_value(parent, child, exploration_constant):
    exploitation_term = child.total_reward / child.visit_count if child.visit_count != 0 else 0
    exploration_term = math.sqrt(math.log(parent.visit_count) / child.visit_count) if child.visit_count != 0 else 0
    return exploitation_term + exploration_constant * exploration_term

########### function for expand
def expand(node):
    legal_moves_list = legal_moves(node.state)
    random_move = random.choice(legal_moves_list)

    #create new child, change turn_player
    child = create_child_node(node, random_move)
    #add child(eren) to node
    node.childeren.append(child)

    return child
########## function for rollout
def rollout(node, player_id):
    roll_out_node = copy.deepcopy(node)
    #key= we only need 1 state
    while non_terminal(roll_out_node):
        roll_out_node = rollout_policy(roll_out_node)
    return result(roll_out_node, player_id)

def non_terminal(node):
    #return False at when sudoku board is full
    if len(legal_moves(node.state)) > 0:
        return True
    else:
        return False

def rollout_policy(node):
    #we are not updating, the list_of_childeren, list of parents, this simulation is inplace
    legal_moves_list = legal_moves(node.state)
    move = random.choice(legal_moves_list)
    points1 = get_points(node.state, move)

    if node.turn_player:  # player 1 to play
        node.state.scores = [node.state.scores[0] + points1 + node.state.scores[1]]
        node.turn_player = False  # set to player 2
    else:
        node.state.scores = [node.state.scores[0] + points1 + node.state.scores[1]]
        node.turn_player = True # set to player 1

    node.state.board.put(move[0], move[1], 1)  # play move on child_board
    return node

def result(node, player_id):
    # 1 point if win
    # 0 points if lose
    if player_id and (node.state.scores[0] > node.state.scores[1]) : #left is winner
        return 1
    else:
        return 0

############ function for backpropegation
def backpropagate(node, result):
    if node.is_root: #still have to create root Node
        return

    # Update the statistics of the current node based on the simulation result
    node.total_reward += result
    node.visit_count += 1
    # Recursively backpropagate to the parent node
    backpropagate(node.parent, result)
######### function for best child

def best_child(root):
    if not root.children:
        return None  # No children to choose from

    # Robust child selection: choose the child with the highest number of visits
    most_robust_child = max(root.children, key=lambda child: child.visits)

    return most_robust_child

