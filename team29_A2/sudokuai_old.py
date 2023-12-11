#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
import copy
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    
    def find_board_before_final_board(self, gamestate):
        state = copy.deepcopy(gamestate)

        state.board = gamestate.initial_board
        last_move = state.moves[-1]
        if len(state.moves) != 0:
            for move in state.moves[:-1]:
                state.board.put(move.i, move.j, move.value)
        return state, last_move

            
    
    def calculate_reward(self, gamestate):
        '''we have the last move and the last game_state in the three, how many points did this move gave?'''
        
        rewards = {0:0, 1:1, 2:3, 3:7}

        #print(gamestate)

        game_state_minus_last_move, last_move = self.find_board_before_final_board(gamestate)
        #print(game_state_minus_last_move)
        
        x = last_move.j #get the last move
        y = last_move.i
        N = gamestate.board.N
        m = gamestate.board.region_height()
        n = gamestate.board.region_width()
                
        gamestate = copy.deepcopy(game_state_minus_last_move)
        
        completed = 0
        filled = 0 # is used to count the amount of filled spots 
        for i in range(N):
            if gamestate.board.get(x, i) != SudokuBoard.empty:
                filled += 1
        if filled == N-1: # if the amount of filled spots is N-1, the row is completed (after filling in the last spot)
            completed += 1
        filled = 0
        for i in range(N):
            if gamestate.board.get(i, y) != SudokuBoard.empty:
                filled += 1
        if filled == N-1:
            completed += 1
        # check region box of sudoku if it is completed
        filled = 0
        region = [[((x + inc_m) % m) + (x // m)*m, ((y + inc_n) % n) + (y // n)*n] for inc_m in range(1,m+1) for inc_n in range(1,n+1)] # for finding the coordinates within the region
        for i, j in region:
            if gamestate.board.get(i, j) != SudokuBoard.empty:
                filled += 1
        if filled == N-1:
            completed += 1
            
        return rewards[completed], last_move
           
        
    def evaluation(self, state, isMaximisingPlayer):
        'updates score for evaluation' 
        current_score = state.scores
        reward, last_move = self.calculate_reward(state) 
        print('move we calculated remward for:', last_move)
        print(isMaximisingPlayer)
        print('current:', current_score)
        print('reward:', reward)
        if isMaximisingPlayer: # I inverted these, because evaluation happens after player swap
            state.scores = [state.scores[0] + reward, state.scores[1]]

        else:
            state.scores = [state.scores[0], state.scores[1] + reward]

        print('after:', state.scores)
            
        return state

    def get_possible_values(self, board, row, col, possible_numbers):
        # Return a set of possible values for the given cell
        possible_values = possible_numbers
        m = board.region_height()  # Number of rows in a region
        n = board.region_width()   # Number of columns in a region

        # Remove values present in the same row and column
        for i in range(board.N):
            if board.get(row, i) in possible_values:
                possible_values.remove(board.get(row, i))
            if board.get(i, col) in possible_values:
                possible_values.remove(board.get(i, col))

        # Remove values present in the same region
        start_row, start_col = m * (row // m), n * (col // n)
        for i in range(start_row, start_row + m):
            for j in range(start_col, start_col + n):
                if board.get(i, j) in possible_values:
                    possible_values.remove(board.get(i, j))

        return possible_values


        
    def getChildren(self, game_state):
        '''return list of states that follow from state, written by Diego'''
        N = game_state.board.N
        m = game_state.board.region_height()
        n = game_state.board.region_width()
        empty_spots = []
        # defines the empty spots on the board
        for i in range(N):
            for j in range(N):
                val = game_state.board.get(i,j)
                if val == 0:
                    empty_spots.append([i,j])
        
        possible_numbers = set(range(1, N+1))
        states = []
        count = 0
        count2= 1
        # in this loop we are going to look at all the possible moves and check if they are valid
        for empty_spot in empty_spots:
            possible_values = self.get_possible_values(game_state.board, empty_spot[0], empty_spot[1], possible_numbers)
            for value in possible_values:
                if TabooMove(empty_spot[0], empty_spot[1], value) not in game_state.taboo_moves:
                    print('amount of legal moves found:', count2)
                    state_copy = copy.deepcopy(game_state)
                    state_copy.board.put(empty_spot[0], empty_spot[1], value)
                    lst_moves = state_copy.moves
                    lst_moves.append(Move(empty_spot[0], empty_spot[1], value))
                    state_copy.moves = lst_moves
                    states.append(state_copy) #store the states
                    count2 +=1
                count += 1

        if count == 0:
            print('-------------------------->warning no moves found<---------------------------------')
        if len(states) ==1:
            print('-----------------------warning lenght of states is 1----------------------------')
        return states

    
    def minimax(self, state, depth, isMaximisingPlayer):
        '''Recursively evaluate nodes in the tree,
        returns the best evaluation value, and board state'''
        if depth == 0: #or self.is_terminal_state(state): , might be bugged tested on 2x2
            return self.evaluation(state, isMaximisingPlayer)  # Return (evaluation score, list containing game_states and moves)
        childeren = self.getChildren(state)
        print(childeren)
        print('the length of childeren:', len(childeren))
        if isMaximisingPlayer:
            value = GameState(state.initial_board, state.board, state.taboo_moves, state.moves, [-999999999,0 ])
            for child in childeren:

                value2 = self.minimax(child, depth - 1, False)

                if value2.scores[0] > value.scores[0]:
                    value = value2
            return value
        else:
            value = GameState(state.initial_board, state.board, state.taboo_moves, state.moves, [0, 999999999])
            for child in childeren:
                value2 = self.minimax(child, depth - 1, True)
                if value2.scores[1] < value.scores[1]:
                    value = value2
            return value

    def is_terminal_state(self, state):
        
        #Diego: prety likelly that this function is bugged idk
        m = state.board.region_height()
        n = state.board.region_width()
        N = state.board.N

        filled = 0

        for i in range(N):
            for j in range(N):
                if state.board.get(i,j) != SudokuBoard.empty:
                    filled += 1
        if filled == m*n:
            return True
        else:
            return False


    def compute_best_move(self, game_state: GameState) -> None:
        #python simulate_game.py --first team29_A1-version2-Diego --second=greedy_player --board=boards/random-3x3.txt --time 1
        #example code showing errors
        
        game_state_orginal = copy.deepcopy(game_state)
        game_state.moves = []
        
        game_state.initial_board = game_state.board
        
        
        N = game_state_orginal.board.N
        max_depth = 0 
        for i in range(N):
            for j in range(N):
                val = game_state_orginal.board.get(i,j)
                if val == 0:
                    max_depth += 1
        #iterate over depths
        for depth in range(1,2):  #chnage depth here
            print('current depth isdepth is:', depth)
            state = self.minimax(game_state, depth, True) 
            #for move in state.moves:
            #    print(move)
            #print('score', state.scores)
            self.propose_move(state.moves[-1])



