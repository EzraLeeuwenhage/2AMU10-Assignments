from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import numpy as np

def update_scores(game_state, move, isMaximisingPlayer):
        """ Evaluate the given game state and return a reward.
        @param gamestate: GameState object 
        @param move: Move object
        @param isMaximisingPlayer: Boolean value that indicates if the player is the maximising player or not in the minimax algorithm
        """
        
        N = game_state.board.N
        m = game_state.board.region_height()
        n = game_state.board.region_width()
        our_agent = game_state.our_agent
        
        
        rewards = {0:0, 1:1, 2:3, 3:7} # rewards mapping
        x = move.i
        y = move.j
        # check if the move completes a row, column or region box
        completed_horizontal = check_row(game_state, x) == (N - 1)
        completed_vertical = check_col(game_state, y) == (N - 1)
        completed_block = check_box(game_state, x, y) == (N - 1) # each of these function returns True (==1) if the move completes the field
        completed = completed_horizontal + completed_vertical + completed_block # sum the boolean values (0 or 1) to get the number of completed fields
        
        # add score to the player that made the move (using who is maximising and our_agent number)
        if isMaximisingPlayer: 
                game_state.scores[our_agent] = game_state.scores[our_agent] + rewards[completed]
        else:
                game_state.scores[not our_agent] = game_state.scores[not our_agent] + rewards[completed]
        
        

def evaluate(game_state: GameState):
        """ 
        Evaluate the given game state by taking score difference of two players
        @param gamestate: GameState object
        @return: score difference between two players """

        our_agent = game_state.our_agent
        return game_state.scores[our_agent] - game_state.scores[not our_agent] # simply return scoredifference of our agent minus the other agent
    
def check_row(game_state, row: int):
        """
        Checks if the given row is completed.
        @param gamestate: GameState object
        @param row: A row value in the range [0, ..., N)
        @return: The amount of nonzero elements in the row.
        """
        N = game_state.board.N
        return np.count_nonzero(game_state.board.squares[N*row:N*(row+1)]) # returns how many nonzero elements exist in the row

def check_col(game_state, col: int):
        """
        Checks if the given column is completed.
        @param gamestate: GameState object
        @param col: A column value in the range [0, ..., N)
        @return: The amount of nonzero elements in the column.
        """
        N = game_state.board.N
        column_indexes = np.arange(col, N**2, N) # get the indexes of the column
        return np.count_nonzero(np.array(game_state.board.squares)[column_indexes]) # returns how many nonzero elements exist in the column

def check_box(game_state, row: int, col: int):
        """
        Checks if the given region box in the sudoku is completed.
        indexes of the region box are converted directly to the indexes of the game_state.board.squares (which is a list)
        @param gamestate: GameState object
        @param row: A row value in the range [0, ..., N)
        @param col: A column value in the range [0, ..., N)
        @return: The amount of nonzero elements in the region box.
        """
        N = game_state.board.N
        m = game_state.board.region_height()
        n = game_state.board.region_width()
        row_region = row // m 
        col_region = col // n 

        region_indexes = [] # make list to append the indexes of the region box
        for height_box in range(m): # loop over the height of the region box (m)
            region_indexes.append(np.arange(height_box*N + row_region*m*N+n*col_region, height_box*N + row_region*m*N+n*col_region + n, 1).tolist()) # use np.arange to get the width of the region box (n) and copy paste this downwards over one area of the block box
        region_indexes = np.array(region_indexes).flatten() # multi dimensional to 1d array
        return np.count_nonzero(np.array(game_state.board.squares)[region_indexes]) # returns amount of nonzero elements
