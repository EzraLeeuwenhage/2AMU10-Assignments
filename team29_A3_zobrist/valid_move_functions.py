from competitive_sudoku.sudoku import SudokuBoard, GameState
import numpy as np
from .evaluate_functions import *

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
