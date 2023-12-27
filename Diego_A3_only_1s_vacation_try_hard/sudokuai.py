#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import copy
import numpy as np
import time
from .evaluate_functions_Diego_changed import *
from .valid_move_functions import *
from .Node_class import *
import math
import random

#done
#to do

#make a better testing framework, that iteraterest based on time left. (we can also do continius move suplying)
#fix lower probality of taboo moves
#this sudoku has no solution issue is what is wrecking us right now.

#algortihm doesn't converge, if visit's per possible moves are to low.



class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def _init_(self):
        super()._init_()

    def compute_best_move(self, game_state: GameState) -> None:
        """ 
        Proposes the best playable move found using minimax within the timespan given by the game settings."""
        t1 = time.time()
        one_state = self.only_1s_game_state(game_state)
        #print(one_state)
        root = create_root_node(one_state, True) # it's our turn to play, so the root node, was the ememy game_state
        best_child = monte_carlo_tree_search(root)
        x = solve_box(game_state, best_child.move)

        self.propose_move(Move(best_child.move[0], best_child.move[1], x))
        t2= time.time()
        print('time taken:', t2-t1)
        most_robust_child = best_child
        print('most robust:', most_robust_child.visit_count, 'reward:', most_robust_child.total_reward)
        print('the ucb of the most robust child is:', ucb_value(root, most_robust_child, 1.414), 'with winrate:', (most_robust_child.total_reward / (0.001 + most_robust_child.visit_count)))
    def only_1s_game_state(self, game_state):
        '''changes all values in the sudoku board to ones'''
        one_state = copy.deepcopy(game_state)
        N = one_state.board.N
        for val1 in range(N):
            for val2 in range(N):
                #getS
                val3 = one_state.board.get(val1, val2)
                if val3 != 0:
                    #overide with 1
                    one_state.board.put(val1, val2, 1)

        return one_state

def possible_moves_box(state, move):
    """Adapted from other code, have to test"""
    n = state.board.N
    still_possible = np.arange(1, n+1)
    #rows
    still_possible = values_in_row(state.board, still_possible, move[0])
    #columns
    still_possible = values_in_column(state.board, still_possible, move[1])
    #regions
    still_possible = values_in_block(state.board, still_possible, move[0], move[1])
    return still_possible

def solve_box(state, move):
    ''''
    select a random possible move for now

    '''
    possilbe_moves = possible_moves_box(state, move)
    return random.choice(possilbe_moves)


# main function for the Monte Carlo Tree Search
def monte_carlo_tree_search(root):
    for i in range(1,100): #1000, itterations
    #while resources_left(time, computational power):
        print('itteration', i)
        leaf = traverse(root) # use uctb to find most interrest note
        expanded_leaf = expand(leaf)
        simulation_result = rollout(expanded_leaf, root.turn_player) # playout a game
        backpropagate(expanded_leaf, simulation_result) # update value's
        #add propose move functionality
        best_child = find_best_child(root)  
        #x = solve_box(root.state, best_child.move)
        #add solve sudoku, later only do it x iterations, also only if move is different!
        #move = Move(best_child.move[0], best_child.move[1], x) #whops?

    return best_child # selects best child

################## function for node traversal
def traverse(node):
    while fully_expanded(node):
        node = best_uct(node)
    # in case no children are present / node is terminal
    return node # pick_unvisited(node.children) or,
    # in case you come to a taboo _sudoku, we don't need this for only's.

def fully_expanded(node):
    # False, if no there are no more childeren,
    return len(node.children) != 0

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
    if child.visit_count != 0: #based on slides
        exploitation_term = child.total_reward / child.visit_count #good reward/visit ratio, winrate
        exploration_term = math.sqrt(math.log(parent.visit_count) / child.visit_count) #good relative_visits_to_parent 
    else:
        exploitation_term = 9999999999999999999999999999999 #inf
        exploration_term = 99999999999999999999999999999999  #convergers to zero

    #exploitation_term = child.total_reward / child.visit_count if child.visit_count != 0 else 0 #here do something else
    #exploration_term = math.sqrt(math.log(parent.visit_count) / child.visit_count) if child.visit_count != 0 else 0
    return exploitation_term + exploration_constant * exploration_term

########### function for expand 
def old_expand(node):
    'only by 1 move'
    legal_moves_list = legal_moves(node.state)

    if len(legal_moves_list) == 0: #don't expand, since there is no expension
        return node
    if len(legal_moves_list) != 1:
        random_move = random.choice(legal_moves_list)
    else:
        random_move = legal_moves_list[0]
    #create new child, change turn_player
    child = create_child_node(node, random_move) #We only expand by 1, for now
    #add child(eren) to node
    node.children.append(child)
    return child
def expand(node):
    'by all moves'
    legal_moves_list = legal_moves(node.state)

    if len(legal_moves_list) == 0: #don't expand, since there is no expension
        return node
    if len(legal_moves_list) > 0:
        count = 0           # let's try expand by 1
        for move in legal_moves_list:
            child = create_child_node(node, move)
            node.children.append(child)
            count += 1
            if count == 1:
                return random.choice(node.children) #returns a random kid 
            #return a random node.
        return random.choice(node.children) #returns a random kid

    else:
        random_move = legal_moves_list[0] #expand by only move left
        child = create_child_node(node, random_move)
        node.children.append(child)
        return child


########## function for rollout
def rollout(node, starting_player):
    roll_out_node = copy.deepcopy(node)
    #key= we only need 1 state
    while non_terminal(roll_out_node.state):
        roll_out_node = rollout_policy(roll_out_node)
    return result(roll_out_node, starting_player)

def non_terminal(state):
    #return False at when sudoku board is full
    if len(legal_moves(state)) > 0:
        return True
    else:
        return False

def rollout_policy(node):
    #we are not updating, the list_of_childeren, list of parents, this simulation is inplace
    legal_moves_list = legal_moves(node.state)
    if len(legal_moves_list) != 0:
        move = random.choice(legal_moves_list)
    else:
        move = legal_moves_list[0]
    points1 = get_points(node.state, move)

    if node.turn_player:  # player 1 to play --> might be bugged 
        node.state.scores = [node.state.scores[0] + points1, node.state.scores[1]]
        node.turn_player = False  # set to player 2
    else:
        node.state.scores = [node.state.scores[0], points1 + node.state.scores[1]]
        node.turn_player = True # set to player 1

    node.state.board.put(move[0], move[1], 1)  # play move on child_board
    return node

def result(node, starting_player):
    # 1 point if win
    # 0 points if lose
    if starting_player and (node.state.scores[0] > node.state.scores[1]) : #left is winner
        return 1
    else:
        return 0

############ function for backpropegation
def backpropagate(node, result):
    node.visit_count += 1
    node.total_reward += result
    # if node.turn_player:
    #     node.total_reward += result
    # else:
    #     node.total_reward -= result
    if node.is_root: #still have to create root Node
        return


    # Recursively backpropagate to the parent node
    backpropagate(node.parent, result)
######### function for best child

def find_best_child(root):
    if not root.children:
        return None  # No children to choose from

    # Robust child selection: choose the child with the highest number of visits
    most_robust_child = max(root.children, key=lambda child: child.visit_count)
    
    #most_robust_child = max(root.children, key=lambda child: child.total_reward / child.visit_count if child.visit_count != 0 else 0)
    for child in root.children:
        print('visits:', child.visit_count, 'reward:', child.total_reward, 'score after move:', child.state.scores, 'with usb_value:', ucb_value(root, child, 1.414), 'with winrate:', (child.total_reward / (0.000000000001 + child.visit_count)))
    print('most robust:', most_robust_child.visit_count, 'reward:', most_robust_child.total_reward)
    print('the ucb of the most robust child is:', ucb_value(root, most_robust_child, 1.414), 'with winrate:', (most_robust_child.total_reward / (0.00000000001 + most_robust_child.visit_count)))
    return most_robust_child

