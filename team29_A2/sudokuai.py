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
        Proposes the best playable move found using minimax within the timespan given by the game settings.

        @param game_state: The state of the current game.
        """
        # store our agent's number to keep track of scores
        game_state.our_agent = game_state.current_player() - 1
        N = game_state.board.N

        children_states = self.get_child_states(game_state, True)

        # if only one move is playable, play the only playable move
        if len(children_states) == 1:
            self.propose_move(children_states[0].moves[-1])
        # else, use minimax to evaluate each possible move
        else:
            for depth in range(1, len(get_empty_squares(game_state.board)) + 1):
                evaluation = -99999999
                alpha = -99999999
                beta = 99999999
                print("\n------------depth: {}------------\n".format(depth))

                i = 0
                for child in children_states:
                    print("\n Evaluation of child {}:".format(i))
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

    def minimax(self, game_state: GameState, depth: int, alpha: int, beta: int, is_maximizing_player: bool):
        """ 
        The minimax function evaluates the game state recursively using the minimax algorithm.

        @param game_state: The current state of the game.
        @param depth: The maximum depth to which the minimax algorithm should evaluate game states.
        @param is_maximizing_player: A boolean value indicating whether to maximize the returned value (True) or minimize it (False).
            
        @return: The value of the evaluated game state.
        """
        if depth == 0 or self.is_terminal_state(game_state.board):
            return evaluate(game_state)

        children_states = self.get_child_states(game_state, is_maximizing_player)

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

    # TODO: we need to update this function to limit the moveset we check 
    def get_child_states(self, game_state: GameState, is_maximizing_player: bool):
        """ 
        Produces all possible child states from the input game state by playing the available moves.

        @param game_state: The current state of the game.
        @param is_maximizing_player: A boolean value indicating whether to maximize the returned value (True) or minimize it (False).
        
        @return: A list of child states.
        """
        children_states = []

        for move in self.get_valid_moves(game_state):
            game_state_copy = copy.deepcopy(game_state)

            game_state_copy.moves.append(move)
            update_scores(game_state_copy, move,
                          is_maximizing_player)  # update scores
            game_state_copy.board.put(
                move.i, move.j, move.value)  # fill in the move
            children_states.append(game_state_copy)
        return children_states

    def get_valid_moves(self, game_state: GameState):
        """ 
        Check valid moves for the current game state.

        @param game_state: The state of the current game.
        @return: List of all valid moves not in Taboo moves.
        """
        N = game_state.board.N
        # Get the indices of empty squares on the board
        empty_squares = get_empty_squares(game_state.board)

        possible_moves = []
        for index in empty_squares:
            row = index // N
            col = index % N
            still_possible = np.arange(1, N+1)
            # Input the values still possible and subtract from it the values already in the row
            possible_row = values_in_row(game_state.board, still_possible, row)
            # Input the values still possible in the row to subtract from it the values already in the column
            possible_col = values_in_column(game_state.board, possible_row, col)
            # Input the values still possible in the row and column to subtract from it the values already in the block
            possible_block = values_in_block(game_state.board, possible_col, row, col)
            # remove 0 from the set of possible values, since we cannot play 0 values
            values_possible = possible_block[possible_block != 0]
            for value in values_possible:
                # if value is not a known taboo move, then it is playable
                if TabooMove(row, col, value) not in game_state.taboo_moves:
                    possible_moves.append(Move(row, col, value))
        return possible_moves
