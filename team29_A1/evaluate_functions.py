from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai

def update_score(game_state, move, isMaximisingPlayer):
    """ Evaluate the given game state and return a reward.
     @param gamestate: GameState object 
     @param move: Move object
     @param score: holds the total score difference between the two players"""
    
    N = game_state.board.N
    m = game_state.board.region_height()
    n = game_state.board.region_width()
    if isMaximisingPlayer:
        score = game_state.score[1]
    else:
        score = game_state.score[0]
    
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

    return score + rewards[completed]

def evaluate(game_state, isMaximisingPlayer):
    if isMaximisingPlayer:
        return game_state.score[0] - game_state.score[1]
    else:
        return game_state.score[1] - game_state.score[0]