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

    def _init_(self):
        super()._init_()

    # N.B. This is a very naive implementation.
    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N
        m = game_state.board.region_height()
        n = game_state.board.region_width()

        #def possible(i, j, value):
        #    return game_state.board.get(i, j) == SudokuBoard.empty \
        #           and not TabooMove(i, j, value) in game_state.taboo_moves

        # defines the empty spots on the board
        def empty(i, j):
            return game_state.board.get(i, j) == SudokuBoard.empty

        #all_moves = [Move(i, j, value) for i in range(N) for j in range(N)
        #             for value in range(1, N+1) if possible(i, j, value)]

        def possible():

            # defines all coordinates in a tuple list that are empty spots on the board
            all_moves = [[i, j] for i in range(N) for j in range(N) if empty(i, j)]
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
            return(possible_moves)
        
        # evaluates the move based on the amount of completed rows, columns and region boxes
        def evaluate(move):
            rewards = {0:0, 1:1, 2:3, 3:7}
            x = move.i
            y = move.j
            completed = 0
            filled = 0 # is used to count the amount of filled spots 
            for i in range(N):
                if game_state.board.get(x, i) != SudokuBoard.empty:
                    filled += 1
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
            return rewards[completed] # convert the amount of filled regions to reward
                    


        possible_moves = possible()
        max_reward = -1
        
        # finds the move with the highest reward
        for move in possible_moves:
            reward = evaluate(move)
            if reward > max_reward:
                max_reward = reward
                best_move = move
        self.propose_move(best_move)
        #move = random.choice(possible_moves)
        #self.propose_move(move)
        #while True:
        #    time.sleep(0.2)
        #    self.propose_move(random.choice(possible_moves))    """ 
     
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