#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from .evaluate_functions import *
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import copy


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """
    def _init_(self):
        super()._init_()

    def compute_best_move(self, game_state: GameState) -> None:
        """ 
        Proposes the best playable move found using minimax within the timespan given by the game settings

        @param game_state the state of the current game
       """
        game_state.our_agent = game_state.current_player() - 1 
        N = game_state.board.N

        # first propose some valid move to play
        #all_moves = self.get_valid_moves(game_state)
        #move = random.choice(all_moves)
        #game_state.our_agent = 
        #self.propose_move(move)
        # call minimax

        # print("start time: {time}".format(time=time.time()))
        
        
        #for depth in range(1,len(self.get_empty_squares(game_state.board))):
        children_states = self.get_child_states(game_state, True)
        # i = 0
        # for child in children_states:
        #     print("Child {}:\n {}".format(i, child))
            # print("Player 1 score: {}".format(child.scores[0]))
            # print("Player 2 score: {}".format(child.scores[1]))
            # print(evaluate(child))
            # i += 1
        
        if len(children_states) > 1:
            for depth in range(1, len(self.get_empty_squares(game_state.board)) + 1):
                evaluation = -99999999
                print("\n------------depth: {}------------\n".format(depth))
                # print("trying for depth: " + str(depth) + "eval: ", end=" ")
                i = 0
                for child in children_states:
                    print("\n Evaluation of child {}:".format(i))
                    new_evaluation = self.minimax(child, depth - 1, False)
                    
                    print("Current highest evaluation: {}".format(evaluation))

                    if new_evaluation is not None:
                        print("Evaluation new subtree {}: {}".format(i, new_evaluation))
                    
                        if new_evaluation > evaluation:
                            evaluation = new_evaluation
                            best_move = child.moves[-1]
                            print("best move update:", best_move)
                    i += 1
                
                self.propose_move(best_move)
        else:
            self.propose_move(children_states[0].moves[-1])
    
    """
     The minimax function takes the gamesstate, maximum depth and a boolean value indicating to either maximize or 
     minimize the returned value.
     @param game_state (GameState object) is the current state of the board with related player scores and moves.
     @param depth the maximum depth =to which the minimax algorithm should evaluate game states
     @param is_maximizing a boolean value indicating whether to maximize the returned value or whether to minimize it.
        A True value means maximizing.

    @return the value of the evaluated gamestate and the correct move to eventually reach that gamestate
       """
    def minimax(self, game_state: GameState, depth: int, is_maximizing_player: bool):
        # print("minimax call, depth {}, ismaximizing: {}\n".format(depth, is_maximizing_player))
        # set a termination guard
        #print('inside minimax; is player maximising:' + str(is_maximizing_player))
        if depth == 0 or self.is_terminal_state(game_state.board):
            # for move in game_state.moves:    
            #     print(move)
            # print(f"{game_state.scores[0]} - {game_state.scores[1]}")
            # print(evaluate(game_state))
            return evaluate(game_state)
        
        children_states = self.get_child_states(game_state, is_maximizing_player)
        
        # check if there are childstates, i.e. check if no taboo move was played
        # if a taboo move was played, do not evaluate subtree
        if not children_states:
            return None

        if is_maximizing_player:
            evaluation = -99999999
            for child_state in children_states:
                # print("Child: \n{}".format(child_state))
                new_evaluation = self.minimax(child_state, depth - 1, False)
                
                if new_evaluation is not None:
                    evaluation = max(evaluation, new_evaluation)

            return evaluation
        else:
            evaluation = 99999999
            for child_state in children_states:
                # print("Child: \n{}".format(child_state))
                new_evaluation = self.minimax(child_state, depth - 1, True)
                
                if new_evaluation is not None:
                    evaluation = min(evaluation, new_evaluation)

            return evaluation
        
    """ 
     Produces all possible child states from the input game state by playing the available moves
       """
    
    def is_terminal_state(self, board: SudokuBoard):
        """
        Evaluates whether the input board is a terminal state, i.e. whether the board is completely filled.
        @param board the state of the sudoku board
        @return True if the board is completely filled, else False
        """
        
        return not np.isin(0, board.squares)
    
    def get_child_states(self, game_state: GameState, is_maximizing_player: bool):
        children_states = []

        for move in self.get_valid_moves(game_state):
            game_state_copy = copy.deepcopy(game_state)

            game_state_copy.moves.append(move)
            update_scores(game_state_copy, move, is_maximizing_player) # update scores
            game_state_copy.board.put(move.i, move.j, move.value) # fill in the move
            children_states.append(game_state_copy)
        return children_states

    """ 
     Get_empty_squares is a function that takes in the current sudoku board and retrieves the list of squares that are not yet filled.
     
     @param board the state of the sudoku board
     @return the set of empty squares on the board
     """
    def get_empty_squares(self, board: SudokuBoard):
        
        zero_indexes = np.where(np.array(board.squares)==0)[0]
        return list(zero_indexes)

    """ 
     Checks if the value in the given square is already present somewhere else in the square's row

     @param row the y coordinate and the value of the square to check for
     @param board the state of the sudoku board
     @return true if the value of square is present somewhere else in the row, else false
       """
    def is_in_row(self, board: SudokuBoard, still_possible: np.array, row: int):
        N = board.N

        row_values = np.array(board.squares[N*row: N*(row+1)])

        return np.setdiff1d(still_possible, row_values)

    """ 
     Checks if the value in the given square is already present somewhere else in the square's column

     @param square the x and y coordinate and the value of the square to check for
     @param board the state of the sudoku board
     @return true if the value of square is present somewhere else in the column, else false
       """
    def is_in_column(self, board: SudokuBoard, still_possible: np.array, col: int):
        N = board.N

        col_values = np.array(board.squares)[np.arange(col, N**2, N)]

        return np.setdiff1d(still_possible, col_values)

    """ 
     Checks if the value in the given square is already present somewhere else in the square's block

     @param square the x and y coordinate and the value of the square to check for
     @param board the state of the sudoku board
     @return true if the value of square is present somewhere else in the block, else false
       """  
    def is_in_block(self, board: SudokuBoard, still_possible: np.array, row: int, col: int):
        N = board.N
        m = board.m
        n = board.n
        row_region = row // m
        col_region = col // n

        region_indices = [] # make list to append the indexes of the region box
        for height_box in range(m): # loop over the height of the region box (m)
            region_indices.append(np.arange(height_box*N + row_region*m*N+n*col_region, height_box*N + row_region*m*N+n*col_region + n, 1).tolist()) # use np.arange to get the width of the region box (n)
        region_indices = np.array(region_indices).flatten()
        region_values = np.array(board.squares)[region_indices]
        return np.setdiff1d(still_possible, region_values)


    def get_valid_moves(self, game_state: GameState):
        """ 
        Check valid moves for the current game state
        @param game_state the state of the current game
        @return list of all valid moves not in Tabboomoves
        """
        N = game_state.board.N
        
        empty_squares = self.get_empty_squares(game_state.board)

        possible_moves = []
        for index in empty_squares:
            row = index // N
            col = index % N
            still_possible = np.arange(1, N+1)
            possible_row = self.is_in_row(game_state.board, still_possible, row)
            possible_col = self.is_in_column(game_state.board, possible_row, col)
            possible_block = self.is_in_block(game_state.board, possible_col, row, col)
            values_possible = possible_block[possible_block != 0]
            for value in values_possible:
                if TabooMove(row, col, value) not in game_state.taboo_moves:
                    possible_moves.append(Move(row, col, value))
        #for move in possible_moves:
        #    print(move.i, move.j, move.value)
        return possible_moves