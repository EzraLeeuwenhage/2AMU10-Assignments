from competitive_sudoku.sudoku import SudokuBoard, GameState
import numpy as np
from .evaluate_functions import *

def check_filling_early_game(self, game_state: GameState):
        """ 
        Checks the filling of the board in early game. 
         @param game_state: The state of the current game. 
         @return: Lists of the filling of the rows, columns and blocks, and the length of these arrays inside."""

        N = game_state.board.N
        m = game_state.board.region_height()
        n = game_state.board.region_width()

        # create lists of the values in each row, column and block, so we can check which values are still possible in an efficient way
        row_filling = []
        len_row_filling = []
        col_filling = []
        len_col_filling = []
        block_filling = []
        len_block_filling = []

        # for each reagion, check which values are still possible and also include length of the list of possible values
        for row in range(N):
            row_filling.append(values_in_row(game_state, row))
            row_filling_nonzero = row_filling[row][row_filling[row] != 0]
            len_row_filling.append(len(row_filling_nonzero))
        for col in range(N):    
            col_filling.append(values_in_column(game_state, col))
            col_filling_nonzero = col_filling[col][col_filling[col] != 0]
            len_col_filling.append(len(col_filling_nonzero))
        
        for row_block in range(n):
            for col_block in range(m):
                block_filling.append(values_in_block(game_state, row_block*m, col_block*n))
        for block_index in range(N):
            block_filling_nonzero = block_filling[block_index][block_filling[block_index] != 0]
            len_block_filling.append(len(block_filling_nonzero))

        return row_filling, col_filling, block_filling, len_row_filling, len_col_filling, len_block_filling
       

def choose_move_early_game(self, game_state: GameState, completion_moves, okay_moves, bad_moves):
    """ 
        Returns the best move in early game from the completion, okay and bad moves lists.
        @param game_state: The state of the current game.
        @param completion_moves: List of completion moves.
    @param okay_moves: List of okay moves.
    @param bad_moves: List of bad moves.
        @return: The best move in early game. """
    # check if there are completion moves, if so, pick the one that fills the fullest block

    if len(completion_moves) > 0:
        highest_block_filling = -1
        for move in completion_moves:
            if check_box(game_state, move.i, move.j) > highest_block_filling:
                best_move = move
        return best_move
    # check if there are okay moves, if so, pick the one that fills the fullest block

    elif len(okay_moves) > 0:
        highest_block_filling = -1
        for move in okay_moves:
            if check_box(game_state, move.i, move.j) > highest_block_filling:
                best_move = move
        return best_move
    # if there are no completion or okay moves, pick a bad move
    else: 
        return bad_moves[0]

def get_empty_squares(board: SudokuBoard):
    """ 
    Get_empty_squares retrieves the list of squares that are not yet filled.

    @param board: The state of the sudoku board.
    @return: The list of indices of empty squares on the board.
    """
    zero_indexes = np.where(np.array(board.squares) == 0)[0]
    return list(zero_indexes)


def values_in_row(game_state: GameState, row: int):
    """ 
    Generates the values which are already present in the row of the square to check

    @param game_state: The state of the sudoku board.
    @param row: The y-coordinate of the square to check.

    @return: Array of possible values excluding those already present in the row.
    """
    N = game_state.board.N
    # take a slice of the 1D list of squares containing all values in the row
    row_values = np.array(game_state.board.squares[N*row: N*(row+1)])
    # return the set-difference between the values possible beforehand and the row values
    return row_values


def values_in_column(game_state: GameState, col: int):
    """ 
    Generates the values which are already present in the column of the square to check

    @param game_state: The state of the sudoku board.
    @param col: The x-coordinate of the square to check.

    @return: Array of possible values excluding those already present in the column.
    """
    N = game_state.board.N
    # take a slice of the 1D list of squares containing all values in the column
    col_values = np.array(game_state.board.squares)[np.arange(col, N**2, N)]
    # return the set-difference between the values possible beforehand and the column values
    return col_values


def values_in_block(game_state: GameState, row: int, col: int):
    """ 
    Generates the values which are already present in the block of the square to check

    @param game_state: The state of the sudoku board.
    @param row: The row-coordinate of the square to check.
    @param col: The check-coordinate of the square to check.

    @return: Array of existing values in the block.
    """
    N = game_state.board.N
    m = game_state.board.m
    n = game_state.board.n
    row_region = row // m
    col_region = col // n

    region_indices = []
    # get the indices of squares in the block
    for height_box in range(m):
        region_indices.append(np.arange(height_box*N + row_region*m*N+n*col_region, height_box*N + row_region *
                              m*N+n*col_region + n, 1).tolist())
    # put the found indices in a 1D array
    region_indices = np.array(region_indices).flatten()
    # take a slice of the 1D list of squares containing all values in the column
    region_values = np.array(game_state.board.squares)[region_indices]
    # return the set-difference between the values possible beforehand and the block values
    return region_values
