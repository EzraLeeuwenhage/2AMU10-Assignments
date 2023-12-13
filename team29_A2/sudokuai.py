#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from .evaluate_functions import *
from .valid_move_functions import *
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
        Proposes the best playable move found using minimax within the timespan given by the game settings. Calls early_game() first and then if there is time left uses minimax_main() to find the best move.
        @param game_state: The state of the current game.
        """
        # store our agent's number to keep track of scores
        game_state.our_agent = game_state.current_player() - 1
        N = game_state.board.N

        # uses early_game strategy first, then minimax if there is time left
        self.early_game(game_state)
        #self.minimax_main(game_state)


    
    def early_game(self, game_state: GameState):
        """ 
        Proposes the best playable move found using early game strategy. Early game strategy tries to play moves that complete regions, and avoids moves that gives the opponent a chance to complete a region. 
        Also selects for moves that are neither the one that reduces the possible moves list the most nor the one that fills the fullest block.
        @param game_state: The state of the current game.
           """
        N = game_state.board.N
        m = game_state.board.region_height()
        n = game_state.board.region_width()

        # completion moves are the moves that complete a region, bad_moves are moves that give the opponent a chance to complete a region, okay_moves are the rest
        completion_moves = []
        bad_moves = []
        okay_moves = []
        
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
        
        # for each empty square check the possible values and if the corresponding move is not taboo, add it to the corresponding list (completion, bad or okay)
        empty_squares = get_empty_squares(game_state.board)
        for empty_square in empty_squares:
            row = empty_square // N
            col = empty_square % N
            block = row // m * m + col // n
            possible_values = np.arange(1, N+1)
            possible_values = np.setdiff1d(possible_values, [row_filling[row], col_filling[col], block_filling[block]])
            if len_row_filling[row] == N-1 or len_col_filling[col] == N-1 or len_block_filling[block] == N-1:
                completion_moves.append(Move(row, col, possible_values[0]))
            if len_row_filling[row] == N-2 or len_col_filling[col] == N-2 or len_block_filling[block] == N-2:
                for value in possible_values:
                    if TabooMove(row, col, value) not in game_state.taboo_moves:
                        bad_moves.append(Move(row, col, value))
            else:
                for value in possible_values:
                    if TabooMove(row, col, value) not in game_state.taboo_moves:
                        okay_moves.append(Move(row, col, value))
        # if a move is a completion move AND a bad move, remove it from the bad moves list
        for move in completion_moves:
            if move in bad_moves:
                completion_moves.remove(move)
        """
        if len(completion_moves) > 0:
            print('\ncompletion moves: ', end = ' ')
            for move in completion_moves:
                #print(move)
                print(move.i, move.j, move.value, end= ', ')
        if len(okay_moves) > 0:
            print('\nokay moves: ', end = ' ')
            for move in okay_moves:
                print(move.i, move.j, move.value, end= ', ')
        if len(bad_moves) > 0:
            print('\nbad moves: ', end = ' ')
            for move in bad_moves:
                print(move.i, move.j, move.value, end= ', ')
        """
        

        # play a completion_move if it exists, else play an okay_move, else play a bad_move.
        # if there are multiple moves in the list, pick the one that fills the fullest block to reduce the followup moveset the most

        if len(completion_moves) > 0:
            self.propose_move(completion_moves[0])
            print('proposed completion move')
            highest_block_filling = -1
            for move in completion_moves:
                if check_box(game_state, move.i, move.j) > highest_block_filling:
                    print('highest block filling: ', check_box(game_state, move.i, move.j))
                    best_move = move
            self.propose_move(best_move)
        elif len(okay_moves) > 0:
            self.propose_move(okay_moves[0])
            print('proposed okay move')
            highest_block_filling = -1
            for move in okay_moves:
                if check_box(game_state, move.i, move.j) > highest_block_filling:
                    best_move = move
            self.propose_move(best_move)
        else: 
            print('proposed bad move')
            self.propose_move(bad_moves[0])
       
    def minimax_main(self, game_state: GameState):
        """ 
        Propose the best playable move with minimax agorithm. minimax_main() calls minimax() to evaluate each possible move and then proposes the move that reduces the possible moves list the most.
          @param game_state: The state of the current game.
          """
        # first get the child states of the current game state
        children_states = self.get_child_states(game_state, True)

        # if only one move is playable, play the only playable move
        if len(children_states) == 1:
            self.propose_move(children_states[0].moves[-1])
        # else, use minimax to evaluate each possible move
        else:
            # iterate over all possible depths, starting from 1
            for depth in range(1, len(get_empty_squares(game_state.board)) + 1):
                evaluation = -99999999
                alpha = -99999999
                beta = 99999999

                # for each possibility, evaluate the game state using minimax recursion
                for child in children_states:
                    
                    new_evaluation = self.minimax(child, depth - 1, alpha, beta, False)


                    # if child did not turn out to be taboo move
                    if new_evaluation is not None:
                        # check if new_evaluation is higher, if so, update evaluation and best_move and reset equally_good_moves.
                        if new_evaluation > evaluation:
                            equally_good_moves = []

                            evaluation = new_evaluation
                            equally_good_moves.append(child.moves[-1])
                        # if there are multiple moves with the same evaluation, add them to equally_good_moves    
                        if new_evaluation == evaluation:
                            equally_good_moves.append(child.moves[-1])

                    
                # if there is only one move in equally_good_moves, play that move
                if len(equally_good_moves) == 1:
                    self.propose_move(equally_good_moves[0])
                # if there is not only one move in equally_good_moves, pick the move that fills the fullest block and reduces the possible moves list the most
                else:
                    highest_block_filling = -1
                    for move in equally_good_moves:
                        if check_box(game_state, move.i, move.j) > highest_block_filling:
                            best_move = move
                    self.propose_move(best_move) # propose the best move
                

    def minimax(self, game_state: GameState, depth: int, alpha: int, beta: int, is_maximizing_player: bool):
        """ 
        The minimax function evaluates the game state recursively using the minimax algorithm. Is called from the minimax_main() function.

        @param game_state: The current state of the game.
        @param depth: The maximum depth to which the minimax algorithm should evaluate game states.
        @param alpha: The alpha value for alpha-beta pruning.
        @param beta: The beta value for alpha-beta pruning.
        @param is_maximizing_player: A boolean value indicating whether to maximize the returned value (True) or minimize it (False).
            
        @return: The evaluation value of the game state.
        """
        # if depth is zero or terminal state, evaluate the game state (recursion base case)
        if depth == 0 or self.is_terminal_state(game_state.board):
            return evaluate(game_state)

        # get the child states of the current game state
        children_states = self.get_child_states(game_state, is_maximizing_player)

        # if depth not zero and not terminal state, but no child states, then taboo move was played
        if not children_states:
            # do not evaluate taboo move
            return None
        # trivially, for the maximising player
        if is_maximizing_player:
            evaluation = -99999999
            for child_state in children_states:
                new_evaluation = self.minimax(child_state, depth - 1, alpha, beta, False)

                # if not an evaluation of taboo move
                if new_evaluation is not None:
                    evaluation = max(evaluation, new_evaluation) # consider max value of evaluation
                    alpha = max(alpha, new_evaluation)
                    # alpha-beta pruning
                    if beta <= alpha:
                        break

            return evaluation
        # if minimizing player:
        else:
            evaluation = 99999999
            for child_state in children_states:
                new_evaluation = self.minimax(child_state, depth - 1, alpha, beta, True)

                # if not an evaluation of taboo move
                if new_evaluation is not None:
                    evaluation = min(evaluation, new_evaluation) # consider min value of evaluation
                    beta = min(beta, new_evaluation)
                    # alpha-beta pruning
                    if beta <= alpha:
                        break

            return evaluation

    def is_terminal_state(self, board: SudokuBoard):
        """ 
        Evaluates whether the input board is a terminal state, i.e., whether the board is completely filled.

        @param board: The state of the sudoku board.
        @return: True if the board is completely filled, else False.
        """
        return not np.isin(0, board.squares)

    
    def get_child_states(self, game_state: GameState, is_maximizing_player: bool):
        """ 
        Produces all possible child states from the input game state by playing the available moves.

        @param game_state: The current state of the game.
        @param is_maximizing_player: A boolean value indicating whether to maximize the returned value (True) or minimize it (False).
        
        @return: A list of child states.
        """
        children_states = []
        # for each possible move, create a child state
        for move in self.get_valid_moves(game_state):
            game_state_copy = copy.deepcopy(game_state) # deepcopy gamestate

            game_state_copy.moves.append(move) # add move to moves list
            update_scores(game_state_copy, move,
                          is_maximizing_player)  # update scores
            game_state_copy.board.put(
                move.i, move.j, move.value)  # fill in the move
            children_states.append(game_state_copy) # add child state to list of child states
        return children_states

    def get_valid_moves(self, game_state: GameState):
        """ 
        Check valid moves for the current game state. 

        @param game_state: The state of the current game.
        @return: List of all valid moves not in Taboo moves.
        """
        N = game_state.board.N
        m = game_state.board.region_height()
        n = game_state.board.region_width()

        # check the filling of the three different region types, so we can check which values are still possible in an efficient way
        row_filling = []
        col_filling = []
        block_filling = []
        for row in range(N):
            row_filling.append(values_in_row(game_state, row))
        for col in range(N):    
            col_filling.append(values_in_column(game_state, col))
        for row_block in range(n):
            for col_block in range(m):
                block_filling.append(values_in_block(game_state, row_block*m, col_block*n))
        
        possible_moves = []
        empty_squares = get_empty_squares(game_state.board)
        # for each emtpy square, check the possible values and if the corresponding move is not taboo, add it to the list of possible moves
        for empty_square in empty_squares:
            row = empty_square // N
            col = empty_square % N
            block = row // m * m + col // n # block index 
            possible_values = np.arange(1, N+1)
            possible_values = np.setdiff1d(possible_values, [row_filling[row], col_filling[col], block_filling[block]])
            for value in possible_values:
                if TabooMove(row, col, value) not in game_state.taboo_moves:
                    possible_moves.append(Move(row, col, value))

        return possible_moves
