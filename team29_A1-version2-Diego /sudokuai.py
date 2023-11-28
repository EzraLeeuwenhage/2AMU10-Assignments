#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import copy #Diego, i added this import idk if allowed
#Diego vesrion, updated 27 november 3:00

#to do is write down all object types in the code, what is xyz
class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

 
    def evaluation(self, evo_score, gamestate):
        '''return numerical evaluation of state, a state is a suduko board state
        board is a board state,
        
        verry naive implementation needs way more work, maybe do this as an experiment on the report,
        
        so for diffent sudoko sizes, and different eval functions.
        things to add = region,
        multipe points.
        
        comment Diego: I just did something quick and random please do this proberly. I think inlcuding game_state.scores is a nice touch, loop is also bugged, doesn't do double points
        
        '''
        rewards = {0:0, 1:1, 2:4, 3:7} #the points according assigment, adding 0.5 to avoid stuff
        
        #keep track of current score's?
        counter_reward = 0
        N = gamestate[0].board.N
        
        # reward counter for 1 empty row value
        #read left to right, so first change column names(j)
        empty = 0 
        empty2= 0
        outer_break = False
        outer_break2 = False
        
        
        for j in range(N):
            for i in range(N):
                value = gamestate[0].board.get(i,j)
                if value == 0:
                    empty += 1
            if empty == 1:
                counter_reward += 1
                outer_break = True
            if outer_break:
                break
            empty = 0
        # reward counter for 1 empty column value
        for i in range(N):
            for j in range(N):
                value = gamestate[0].board.get(i,j)
                if value == 0:
                    empty2 += 1
            if empty2 == 1:
                counter_reward += 1
                outer_break2 = True
            if outer_break2:
                break
            
            empty2 = 0
         
        #score_metric= gamestate.scores[0] - gamestate.scores[1] #to do is save this somewhere
        evalutation = rewards[counter_reward] #+ score_metric

        
        return (evalutation, gamestate) #where evalution should be a score/value
        
    
    def getChildren(self, evo_score, game_state):
        '''return list of states that follow from state, written by Diego'''
        N = game_state[0].board.N
        m = game_state[0].board.region_height()
        n = game_state[0].board.region_width()

        # defines the empty spots on the board
        def empty(i, j):
            return game_state[0].board.get(i, j) == SudokuBoard.empty
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
                val = game_state[0].board.get(mov[0], mov[1])
                if val in possible_val:
                    possible_val.remove(val)
            # add the move to the possible moves list
            for value in possible_val:
                if TabooMove(a[0], a[1], value) not in game_state[0].taboo_moves:
                    possible_moves.append(Move(a[0], a[1], value))
        
        states = []
        
        for move in possible_moves:
            game_state_board_copy = copy.deepcopy(game_state[0]) #copy gamestate
            #append move to moves
            lst_moves = game_state[1]
            lst_moves.append(move) #append move to list of moves
            #do move on sudoko board
            game_state_board_copy.board.put(move.i, move.j, move.value)
            #add the updated game_state_to_list
            states.append([game_state_board_copy, lst_moves]) #store the move 
            #print(' the move  is ', move)
            #print(' the possible moves are', possible_moves)
        
        
        return (evo_score, states) #numeric, list containing game states and list of  moves
    
    def minimax(self, state, depth, isMaximisingPlayer, evo_score=0):
        '''recursively evaluate nodes in tree, 
        
        returns the best evaluation value, and board state'''
        #result = [0,state] #this might be a mistake putting result to initial state
        #print('the current depth is:', depth, ' the current score is:', evo_score)
        if depth == 0: #or state.isFinished: , the state is finished part comes later
            return self.evaluation(evo_score, state) #return (evalution score, list coitinging game_states and mvoes)
        
        evo_score, childeren = self.getChildren(evo_score, state) #state = [[states],[moves]] 
        
        if isMaximisingPlayer:
            evo_score = -999999999 # -inf
            value = -999999999 # -inf
            for child in childeren:  
                
                evo_score, state = self.minimax(child, depth-1, False, evo_score)
                value = max(value, evo_score) # value is the evaluation function value
        
            return (value, state) #evaluation score, state, move_history_game_state
        else:
            evo_score = 999999999 # + inf 
            value = 999999999 # + inf 
            for child in childeren:
                evo_score, state = self.minimax(child, depth-1, True, evo_score)
                value = min(value, evo_score)
            return (value, state)

    
#         def find_move(self, state, minmax_and_state, depth):
#             'Diego: takes the minmax value and turns it into a move propropoal for the board'

#             #idea1 = track all tree paths
#             N = state.board.N
#             count = 0 
#             for i in range(N):
#                 for j in range(N):
#                     val1 = state.board.get(i,j)
#                     val2 = minmax_and_state[1].board.get(i,j)
#                     if (val1 != val2):
#                         if val2 != 0:
#                             best_move = Move(i, j, val2)
#                             return best_move
#             print('best move not found')



    
    def compute_best_move(self, game_state: GameState) -> None:
        game_state_orginal = copy.deepcopy(game_state)
        N = game_state.board.N
        max_depth = 0 
        for i in range(N):
            for j in range(N):
                val = game_state.board.get(i,j)
                if val == 0:
                    max_depth += 1
        
        #iterate over depths
        for depth in range(1,7): #depth has to be even?? 
            if depth <= max_depth:
                print('Depth is: ', depth)
#                 print('max_depth is', max_depth)
                evo_valu_and_move_hist = self.minimax([game_state, []], depth, True) #depth = 3 for now #maximisingplayer=True
                #print(' result this depth, value: ', evo_valu_and_move_hist[0], ' move: ', evo_valu_and_move_hist[1])
                print(' first in list: ', evo_valu_and_move_hist[1][1][0])
                move1 = evo_valu_and_move_hist[1][1][0]
                #print(' last in list', evo_valu_and_move_hist[1][1][-1])
                #print(' the proposed state is:', evo_valu_and_move_hist[1])
                #move = self.find_move(game_state_orginal, value_min_max, depth)
                self.propose_move(move1)
        

        
     
#started at 15:40
#ended at 3:30