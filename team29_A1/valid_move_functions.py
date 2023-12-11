from competitive_sudoku.sudoku import SudokuBoard
import numpy as np

def get_empty_squares(board: SudokuBoard):
    """ 
    Get_empty_squares retrieves the list of squares that are not yet filled.

    @param board: The state of the sudoku board.
    @return: The list of indices of empty squares on the board.
    """
    zero_indexes = np.where(np.array(board.squares) == 0)[0]
    return list(zero_indexes)

def values_in_row(board: SudokuBoard, still_possible: np.array, row: int):
    """ 
    Generates the values which are already present in the row of the square to check

    @param board: The state of the sudoku board.
    @param still_possible: An array of still possible values.
    @param row: The y-coordinate of the square to check.

    @return: Array of possible values excluding those already present in the row.
    """
    N = board.N
    # take a slice of the 1D list of squares containing all values in the row
    row_values = np.array(board.squares[N*row: N*(row+1)])
    # return the set-difference between the values possible beforehand and the row values
    return np.setdiff1d(still_possible, row_values)


def values_in_column(board: SudokuBoard, still_possible: np.array, col: int):
    """ 
    Generates the values which are already present in the column of the square to check

    @param board: The state of the sudoku board.
    @param still_possible: An array of still possible values.
    @param col: The x-coordinate of the square to check.

    @return: Array of possible values excluding those already present in the column.
    """
    N = board.N
    # take a slice of the 1D list of squares containing all values in the column
    col_values = np.array(board.squares)[np.arange(col, N**2, N)]
    # return the set-difference between the values possible beforehand and the column values
    return np.setdiff1d(still_possible, col_values)


def values_in_block(board: SudokuBoard, still_possible: np.array, row: int, col: int):
    """ 
    Generates the values which are already present in the block of the square to check

    @param board: The state of the sudoku board.
    @param still_possible: An array of still possible values.
    @param row: The y-coordinate of the square to check.
    @param col: The x-coordinate of the square to check.

    @return: Array of possible values excluding those already present in the block.
    """
    N = board.N
    m = board.m
    n = board.n
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
    region_values = np.array(board.squares)[region_indices]
    # return the set-difference between the values possible beforehand and the block values
    return np.setdiff1d(still_possible, region_values)
