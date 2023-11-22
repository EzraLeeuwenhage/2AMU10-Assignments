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
        m = game_state.board.region_height()
        n = game_state.board.region_width()

        #def possible(i, j, value):
        #    return game_state.board.get(i, j) == SudokuBoard.empty \
        #           and not TabooMove(i, j, value) in game_state.taboo_moves

        # defines the empty spots on the board
        def possible(i, j):
            return game_state.board.get(i, j) == SudokuBoard.empty

        #all_moves = [Move(i, j, value) for i in range(N) for j in range(N)
        #             for value in range(1, N+1) if possible(i, j, value)]

        # defines all coordinates in a tuple list that are empty spots on the board
        all_moves = [[i, j] for i in range(N) for j in range(N) if possible(i, j)]
        #move = random.choice(all_moves)
        possible_moves = []
        # in this loop we are going to look at all the possible moves and check if they are valid
        for a in all_moves:
            # this is a list of 1 to N
            possible_val = [i for i in range(1, N+1)]

            # this list contains all vertical, horizontal and region coordinates that we need to check 
            move_check = [
                    [(a[0] + inc_i) % N, a[1]] for inc_i in range(1,N)] + [
                    [a[0], (a[1] + inc_j) % N] for inc_j in range(1,N)] + [
                    [((a[0] + inc_m) % m) + (a[0] // m)*m, ((a[1] + inc_n) % n) 
                     + (a[1] // n)*n]
                     for inc_m in range(1,m) for inc_n in range(1,n)
                    ]
            # retrieve values of the coordinates from move_check and remove the value from the possible value list
            for mov in move_check:
                val = game_state.board.get(mov[0], mov[1])
                if val in possible_val:
                    possible_val.remove(val)
            # add the move to the possible moves list
            for value in possible_val:
                if TabooMove(a[0], a[1], value) not in game_state.taboo_moves:
                    possible_moves.append(Move(a[0], a[1], value))

        #for a in possible_moves:    
        #    print(a)

        move = random.choice(possible_moves)
        self.propose_move(move)
        while True:
            time.sleep(0.2)
            self.propose_move(random.choice(possible_moves))

