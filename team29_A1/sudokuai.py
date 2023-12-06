#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from .evaluate_functions import evaluate
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """
    def _init_(self):
        super()._init_()

    """ 
     Proposes the best playable move found using minimax within the timespan given by the game settings

     @param game_state the state of the current game
       """
    def compute_best_move(self, game_state: GameState) -> None:
        depth = 3

        evaluation, move = self.minimax(game_state, depth, True)
        # print(evaluation)
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
        if depth == 0 or not self.get_empty_squares(game_state.board) or not self.get_child_states(game_state):
            return evaluate(game_state), #what move do i pass along here?
        
        children_states = self.get_child_states(game_state)

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
    def get_child_states(self, game_state: GameState):

        # make a list of gamestates from the valid moves that can be played from the input state using getvalidmoves()
        # uses update_scores() to update all the new game state scores after a move was played 

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

     @param square the x and y coordinate and the value of the square to check for
     @param board the state of the sudoku board
     @return true if the value of square is present somewhere else in the row, else false
       """
    def is_in_row():
        return

    """ 
     Checks if the value in the given square is already present somewhere else in the square's column

     @param square the x and y coordinate and the value of the square to check for
     @param board the state of the sudoku board
     @return true if the value of square is present somewhere else in the column, else false
       """
    def is_in_column():
        return

    """ 
     Checks if the value in the given square is already present somewhere else in the square's block

     @param square the x and y coordinate and the value of the square to check for
     @param board the state of the sudoku board
     @return true if the value of square is present somewhere else in the block, else false
       """
    def is_in_block():
        return

    """ 
     Checks if the value played in a move is neither illegal, nor taboo
     
     @param game_state the state of the current game
     @param move the move which needs to be checked for validity
     @return true if the input move is a valid move, i.e. if the move is not illegal and not a taboo move, else false
       """
    def is_valid_move(self, move: Move, game_state: GameState, value: int):
        valid = False

        # check if the move is illegal
        # check if the move is taboo

        return valid

    """ 
     Gets all valid moves from a game state
       """
    def get_valid_moves(self, game_state: GameState):

        # for loop for all empty squares checking the playable moves using isvalidmove() and getemptysquares()

        return

    # def possible(self, game_state: GameState):
    #     N = game_state.board.N
    #     m = game_state.board.region_height()
    #     n = game_state.board.region_width()

    #     # defines all coordinates in a tuple list that are empty spots on the board
    #     all_moves = [[i, j]
    #                  for i in range(N) for j in range(N) if self.empty(i, j)]
    #     # move = random.choice(all_moves)
    #     possible_moves = []
    #     # in this loop we are going to look at all the possible moves and check if they are valid
    #     for a in all_moves:
    #         # this is a list of 1 to N
    #         possible_val = [i for i in range(1, N+1)]

    #         # this list contains all vertical, horizontal and region coordinates that we need to check
    #         move_check = [
    #             [(a[0] + inc_i) % N, a[1]] for inc_i in range(1, N)] + [
    #             [a[0], (a[1] + inc_j) % N] for inc_j in range(1, N)] + [
    #             [((a[0] + inc_m) % m) + (a[0] // m)*m, ((a[1] + inc_n) % n)
    #              + (a[1] // n)*n]
    #                 for inc_m in range(1, m) for inc_n in range(1, n)
    #         ]
    #         # retrieve values of the coordinates from move_check and remove the value from the possible value list
    #         for mov in move_check:
    #             val = game_state.board.get(mov[0], mov[1])
    #             if val in possible_val:
    #                 possible_val.remove(val)
    #         # add the move to the possible moves list
    #         for value in possible_val:
    #             if TabooMove(a[0], a[1], value) not in game_state.taboo_moves:
    #                 possible_moves.append(Move(a[0], a[1], value))

    #     # for a in possible_moves:
    #     #    print(a)
    #     return (possible_moves)
