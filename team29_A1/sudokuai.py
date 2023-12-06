#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from .evaluate_functions import *
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """
    max_depth = 3

    def _init_(self):
        super()._init_()

    def compute_best_move(self, game_state: GameState) -> None:
        """ 
        Proposes the best playable move found using minimax within the timespan given by the game settings

        @param game_state the state of the current game
       """
        N = game_state.board.N

        self.get_valid_moves(game_state)

        evaluation, move = self.minimax(game_state, self.max_depth, True)
        self.propose_move(move)

    """
     The minimax function takes the gamesstate, maximum depth and a boolean value indicating to either maximize or 
     minimize the returned value.
     @param game_state (GameState object) is the current state of the board with related player scores and moves.
     @param depth the maximum depth =to which the minimax algorithm should evaluate game states
     @param is_maximizing a boolean value indicating whether to maximize the returned value or whether to minimize it.
        A True value means maximizing.

    @return the value of the evaluated gamestate and the correct move to eventually reach that gamestate
       """
    def minimax(self, game_state: GameState, depth: int, is_maximizing: bool):
        # set a termination guard
        if depth == 0 and not self.is_terminal_state(game_state.board):
            return evaluate(game_state), #what move do i pass along here?
        
        children_states = self.get_child_states(game_state)
        print()
        if is_maximizing:
            evaluation = -99999999
            move = None
            for child_state in children_states:
                new_evaluation = self.minimax(child_state, depth - 1, False)

                if new_evaluation > evaluation:
                    evaluation = new_evaluation
                    move = child_state.moves[-1] # I'm not sure if this move passing is actually correct
            
            return evaluation, move
        
        if not is_maximizing:
            evaluation = 99999999
            move = None
            for child_state in children_states:
                new_evaluation = evaluation, self.minimax(child_state, depth - 1, True)

                if new_evaluation > evaluation:
                    evaluation = new_evaluation
                    move = child_state.moves[-1]

            return evaluation, move
        
    """ 
     Produces all possible child states from the input game state by playing the available moves
       """
    
    def is_terminal_state(self, board: SudokuBoard):
        """
        Evaluates whether the input board is a terminal state, i.e. whether the board is completely filled.
        @param board the state of the sudoku board
        @return True if the board is completely filled, else False
        """
        return SudokuBoard.empty not in board.squares
    def get_child_states(self, game_state: GameState):

        # make a list of gamestates from the valid moves that can be played from the input state using getvalidmoves()
        # uses update_scores() to update all the new game state scores after a move was played 

        # update the board
        # update the move list of game state

        return

    """ 
     Get_empty_squares is a function that takes in the current sudoku board and retrieves the list of squares that are not yet filled.
     
     @param board the state of the sudoku board
     @return the set of empty squares on the board
     """
    def get_empty_squares(self, board: SudokuBoard):
        empty_squares = []

        for i in range(board.board_height()):
            for j in range(board.board_width()):
                if board.get(i, j) == SudokuBoard.empty:
                    empty_squares.append((i, j))

        return empty_squares


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
        row_region = row // N
        col_region = col // N

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
        still_possible = np.arange(1, N+1)
        empty_squares = self.get_empty_squares(game_state.board)

        possible_moves = list()
        for x, y in empty_squares:
            possible_row = self.is_in_row(game_state.board, still_possible, x)
            possible_col = self.is_in_column(game_state.board, possible_row, y)
            possible_block = self.is_in_block(game_state.board, possible_col, x, y)
            # enter in the line below this a piece of code that removes 0 from the numpy array
            values_possible = possible_block[possible_block != 0]
            for value in values_possible:
                if TabooMove(x, y, value) not in game_state.taboo_moves:
                    possible_moves.append(Move(x, y, value))
        for move in possible_moves:
            print(move.i, move.j, move.value)
        return possible_moves
        

    def possible(self, game_state: GameState):
        N = game_state.board.N
        m = game_state.board.region_height()
        n = game_state.board.region_width()

        # defines all coordinates in a tuple list that are empty spots on the board
        all_moves = [[i, j]
                     for i in range(N) for j in range(N) if self.empty(i, j)]
        # move = random.choice(all_moves)
        possible_moves = []
        # in this loop we are going to look at all the possible moves and check if they are valid
        for a in all_moves:
            # this is a list of 1 to N
            possible_val = [i for i in range(1, N+1)]

            # this list contains all vertical, horizontal and region coordinates that we need to check
            move_check = [
                [(a[0] + inc_i) % N, a[1]] for inc_i in range(1, N)] + [
                [a[0], (a[1] + inc_j) % N] for inc_j in range(1, N)] + [
                [((a[0] + inc_m) % m) + (a[0] // m)*m, ((a[1] + inc_n) % n)
                 + (a[1] // n)*n]
                    for inc_m in range(1, m) for inc_n in range(1, n)
            ]
            # retrieve values of the coordinates from move_check and remove the value from the possible value list
            for mov in move_check:
                val = game_state.board.get(mov[0], mov[1])
                if val in possible_val:
                    possible_val.remove(val)
            # add the move to the possible moves list
            for value in possible_val:
                if TabooMove(a[0], a[1], value) not in game_state.taboo_moves:
                    possible_moves.append(Move(a[0], a[1], value))

        # for a in possible_moves:
        #    print(a)
        return (possible_moves)
