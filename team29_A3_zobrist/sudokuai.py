#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from .evaluate_functions import *
from .valid_move_functions import *
from .zobrist import *
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import copy


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """
    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        """ 
        Proposes the best playable move found using minimax within the timespan given by the game settings.

        @param game_state: The state of the current game.
        """
        # store our agent's number to keep track of scores
        game_state.our_agent = game_state.current_player() - 1
        N = game_state.board.N

        # retreive previously stored data 
        saved_data: ZobristData = self.load()
        
        # create new data object in case no previous data exists
        if (not saved_data):
            # create an object to store the data in (must be a single object due to the implementation of save mechanic)
            zobrist_data = ZobristData()
            # initialize an empty hash table (python dictonary) for storing the previously calculated game states 
            zobrist_data.zobrist_hash_keys = dict()
            # initialize N^3 64-bit values for generating hash keys from computed game states
            zobrist_data.zobrist_values = initialize_zobrist_values(game_state.initial_board)

            # print(zobrist_data.zobrist_values)

            # hash_key = hash_key_from_board(zobrist_data.zobrist_values, game_state.board)

            # zobrist_data.zobrist_hash_keys[hash_key] = evaluate(game_state)

            self.save(zobrist_data)
            saved_data = zobrist_data
        
        print(f"Saved hash keys: {saved_data.zobrist_hash_keys}\n Saved zobrist values: {saved_data.zobrist_values}")

        children_states = self.get_child_states(game_state, True, saved_data.zobrist_values)

        # for child in children_states:
        #     hash_key = hash_key_from_board(saved_data.zobrist_values, child.board)
        #     board_evaluation = evaluate(child)
        #     saved_data.zobrist_hash_keys[hash_key] = board_evaluation

        # print(saved_data.zobrist_hash_keys)

        # if only one move is playable, play the only playable move
        if len(children_states) == 1:
            self.propose_move(children_states[0].moves[-1])
        # else, use minimax to evaluate each possible move
        else:
            for depth in range(1, len(get_empty_squares(game_state.board)) + 1):
                evaluation = -99999999
                alpha = -99999999
                beta = 99999999
                # print("\n------------depth: {}------------\n".format(depth))

                i = 0
                for child in children_states:
                    # print("\n Evaluation of child {}:".format(i))
                    new_evaluation = self.minimax(child, depth - 1, alpha, beta, False)

                    # print("Current highest evaluation: {}".format(evaluation))

                    # if child did not turn out to be taboo move
                    if new_evaluation is not None:
                        # print("Evaluation new subtree {}: {}".format(i, new_evaluation))

                        if new_evaluation > evaluation:
                            evaluation = new_evaluation
                            best_move = child.moves[-1]
                            # print("best move update:", best_move)
                    i += 1

                self.propose_move(best_move)

    def minimax(self, game_state: GameState, depth: int, alpha: int, beta: int, is_maximizing_player: bool, saved_data: ZobristData):
        """ 
        The minimax function evaluates the game state recursively using the minimax algorithm.

        @param game_state: The current state of the game.
        @param depth: The maximum depth to which the minimax algorithm should evaluate game states.
        @param is_maximizing_player: A boolean value indicating whether to maximize the returned value (True) or minimize it (False).
            
        @return: The value of the evaluated game state.
        """
        print(f"passed gamestate has hash_key attribute: {game_state.hash_key}")
        # TODO: if state reached previously in calculations (game state is in hash table), return evaluation in hash table
        if (game_state.hash_key in saved_data.zobrist_hash_keys):
            print(f"already encountered {game_state.hash_key}")
            return saved_data.zobrist_hash_keys[game_state.hash_key]

        if depth == 0 or self.is_terminal_state(game_state.board):
            return evaluate(game_state)

        children_states = self.get_child_states(game_state, is_maximizing_player, saved_data.zobrist_values)

        # if depth not zero and not terminal state, but no child states, then taboo move was played
        if not children_states:
            # do not evaluate taboo move
            return None

        if is_maximizing_player:
            evaluation = -99999999
            for child_state in children_states:
                new_evaluation = self.minimax(child_state, depth - 1, alpha, beta, False)

                # if not an evaluation of taboo move
                if new_evaluation is not None:
                    evaluation = max(evaluation, new_evaluation)
                    alpha = max(alpha, new_evaluation)
                    if beta <= alpha:
                        # print("\nPrune maximizing\n")
                        break

            return evaluation
        else:
            evaluation = 99999999
            for child_state in children_states:
                new_evaluation = self.minimax(child_state, depth - 1, alpha, beta, True)

                # if not an evaluation of taboo move
                if new_evaluation is not None:
                    evaluation = min(evaluation, new_evaluation)
                    beta = min(beta, new_evaluation)
                    if beta <= alpha:
                        # print("\nPrune minimizing\n")
                        break

            return evaluation

    def is_terminal_state(self, board: SudokuBoard):
        """ 
        Evaluates whether the input board is a terminal state, i.e., whether the board is completely filled.

        @param board: The state of the sudoku board.
        @return: True if the board is completely filled, else False.
        """
        return not np.isin(0, board.squares)

    def get_child_states(self, game_state: GameState, is_maximizing_player: bool, zobrist_values):
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
            update_scores(game_state_copy, move, is_maximizing_player)  # update scores
            game_state_copy.board.put(move.i, move.j, move.value)  # fill in the move
            game_state_copy.hash_key = hash_key_from_board(zobrist_values, game_state_copy.board)
            print(f"successfully added hash_key: {game_state_copy.hash_key}")
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
