from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import numpy as np

def get_points(game_state, move):
        """ Evaluate the given game state and return a reward.
        @param gamestate: GameState object 
        @param move: Move object
        @param isMaximisingPlayer: Boolean value that indicates if the player is the maximising player or not in the minimax algorithm"""
        
        N = game_state.board.N

        
        rewards = {0:0, 1:1, 2:3, 3:7}
        x = move[0]
        y = move[1]
        completed_horizontal = check_row(game_state, x) == (N - 1)
        completed_vertical = check_col(game_state, y) == (N - 1)
        completed_block = check_box(game_state, x, y) == (N - 1) # each of these function returns True (==1) if the move completes the field
        completed = completed_horizontal + completed_vertical + completed_block # if the move completes more than one field, this is counted as one completed field
        #print(completed_horizontal, completed_vertical, completed_block, completed)
        return rewards[completed]

def evaluate(game_state: GameState):
        """ 
        Evaluate the given game state by taking score difference of two players
        @param gamestate: GameState object """

        our_agent = game_state.our_agent
        return game_state.scores[our_agent] - game_state.scores[not our_agent]
    
def check_row(game_state, row: int):
        """
        Checks if the given row is completed.
        @param row: A row value in the range [0, ..., N)
        @return: True if the row is completed, False otherwise.
        """
        N = game_state.board.N
        return np.count_nonzero(game_state.board.squares[N*row:N*(row+1)]) # if N-1 nonzero elements exist before filling in the last spot, this move completes the row

def check_col(game_state, col: int):
        """
        Checks if the given column is completed.
        @param col: A column value in the range [0, ..., N)
        @return: True if the row is completed, False otherwise.
        """
        N = game_state.board.N
        column_indexes = np.arange(col, N**2, N) # get the indexes of the column
        return np.count_nonzero(np.array(game_state.board.squares)[column_indexes]) # if N-1 nonzero elements exist before filling in the last spot, this move completes the column

def check_box(game_state, row: int, col: int):
        """
        Checks if the given region box in the sudoku is completed.
        indexes of the region box are converted directly to the indexes of the game_state.board.squares (which is a list)
        @param row: A row value in the range [0, ..., N)
        @param col: A column value in the range [0, ..., N)
        @return: True if the row is completed, False otherwise.
        """
        N = game_state.board.N
        m = game_state.board.region_height()
        n = game_state.board.region_width()
        row_region = row // m 
        col_region = col // n 

        region_indexes = [] # make list to append the indexes of the region box
        for height_box in range(m): # loop over the height of the region box (m)
            region_indexes.append(np.arange(height_box*N + row_region*m*N+n*col_region, height_box*N + row_region*m*N+n*col_region + n, 1).tolist()) # use np.arange to get the width of the region box (n)
        region_indexes = np.array(region_indexes).flatten() 
        return np.count_nonzero(np.array(game_state.board.squares)[region_indexes]) # if N-1 nonzero elements exist before filling in the last spot, this move completes the region
