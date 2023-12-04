#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    # N.B. This is a very naive implementation.
    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N

        def possible(i, j, value):
            return game_state.board.get(i, j) == SudokuBoard.empty \
                   and not TabooMove(i, j, value) in game_state.taboo_moves

        all_moves = [Move(i, j, value) for i in range(N) for j in range(N)
                     for value in range(1, N+1) if possible(i, j, value)]
        move = random.choice(all_moves)
        self.propose_move(move)
        while True:
            time.sleep(0.2)
            self.propose_move(random.choice(all_moves))

    """ 
     The minimax function takes the gamesstate, maximum depth and a boolean value indicating to either maximize or 
     minimize the returned value.
     @param game_state (GameState object) is the current state of the board with related player scores and moves.
     @param depth the maximum depth =to which the minimax algorithm should evaluate game states
     @param maximize a boolean value indicating whether to maximize the returned value or whether to minimize it.
        A True value means maximizing.

    @return the value of the evaluated gamestate and the correct move to eventually reach that gamestate
       """
    def minimax(game_state: GameState, depth: int, maximize: bool):
        return 