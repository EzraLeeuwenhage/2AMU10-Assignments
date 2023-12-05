from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import numpy as np

def update_score(game_state, move, isMaximisingPlayer):
    """ Evaluate the given game state and return a reward.
     @param gamestate: GameState object 
     @param move: Move object
     @param score: holds the total score difference between the two players"""
    
    N = game_state.board.N
    m = game_state.board.region_height()
    n = game_state.board.region_width()
    
    
    
    rewards = {0:0, 1:1, 2:3, 3:7}
    x = move.i
    y = move.j
    completed = 0
    filled = 0 # is used to count the amount of filled spots 
    for i in range(N):
        if game_state.board.get(x, i) != SudokuBoard.empty:
            filled += 1

    
    print(check_row(game_state, x))
    print(check_col(game_state, y))
    print(check_box(game_state, x, y))
    
    if filled == N-1: # if the amount of filled spots is N-1, the row is completed (after filling in the last spot)
        completed += 1
    filled = 0
    for i in range(N):
        if game_state.board.get(i, y) != SudokuBoard.empty:
            filled += 1
    if filled == N-1:
        completed += 1
    # check region box of sudoku if it is completed
    filled = 0
    region = [[((x + inc_m) % m) + (x // m)*m, ((y + inc_n) % n) + (y // n)*n] for inc_m in range(1,m+1) for inc_n in range(1,n+1)] # for finding the coordinates within the region
    for i, j in region:
        if game_state.board.get(i, j) != SudokuBoard.empty:
            filled += 1
    if filled == N-1:
        completed += 1

    if isMaximisingPlayer:
        game_state.scores[0] = game_state.scores[0] + rewards[completed]
    else:
        game_state.scores[1] = game_state.scores[1] + rewards[completed]


def evaluate(game_state):
        return game_state.scores[0] - game_state.scores[1]
    
def check_row(game_state, row: int):
        """
        Checks if the given row is completed.
        @param row: A row value in the range [0, ..., N)
        @return: True if the row is completed, False otherwise.
        """
        N = game_state.board.N
        return game_state.board.squares[N*row:N*(row+1)].count(SudokuBoard.empty) == 1

def check_col(game_state, col: int):
        """
        Checks if the given column is completed.
        @param col: A column value in the range [0, ..., N)
        @return: True if the row is completed, False otherwise.
        """
        N = game_state.board.N
        column_indexes = np.arange(col, N**2, N) # get the indexes of the column
        return np.count_nonzero(np.array(game_state.board.squares)[column_indexes]) == N - 1

def check_box(game_state, row: int, col: int):
        """
        Checks if the given region box in the sudoku is completed.
        @param row: A row value in the range [0, ..., N)
        @param col: A column value in the range [0, ..., N)
        @return: True if the row is completed, False otherwise.
        """
        N = game_state.board.N
        m = game_state.board.region_height()
        n = game_state.board.region_width()
        print(N, m, n)
        region = [[((row + inc_m) % m) + (row // m)*m, ((col + inc_n) % n) + (col // n)*n] for inc_m in range(1,m+1) for inc_n in range(1,n+1)] # for finding the coordinates within the region
        return np.count_nonzero(np.array(game_state.board.squares)[region]) == N - 1