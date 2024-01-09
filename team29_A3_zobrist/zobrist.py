import numpy as np
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard

class ZobristData():
    """
    Holds all information that needs to be stored between turns for the zobrist hashing algorithm to work
    """
    def __init__(self):
        # An empty dictionary to map 64-bit values to Gamestates
        self.zobrist_hash_keys = dict()

        # A 2D NumPy array containing 64-bit values, initialized to None as sudoku dimentions are needed for numpy array
        self.zobrist_values = None

def generate_unique_random_numbers(N):
    """
    Function to abstract from unique random number generation.
    @param N: region size of sudoku board
    @return unique_random_numbers: 2D array of shape (N^2, N) containing unique and random 64-bit values
    """
    # Generate N^3 unique random 64-bit integers
    unique_random_numbers = np.random.randint(0, 2**64, N**3, dtype=np.uint64)

    # Reshape the array to a 2D array with dimensions (N^2, N)
    unique_random_numbers_2d = unique_random_numbers.reshape((N**2, N))

    return unique_random_numbers_2d

def initialize_zobrist_values(initial_board: SudokuBoard):
    """
    Function to initialize the 64-bit values for generating zobrist hash keys, using generate_unique_random_numbers().
    There will be N*N*N unique values, N unique values for each square in the board. 
    These values will uniquely represent all possible values in each square.
    In other words, for each possible (square, value) tuple an associated 64-bit value is generated to uniquely represent it.

    @param initialboard: initial_board attribute of the game state object
    @return 2D numpy array of length N^2 with each index containing N values 
    """
    N = initial_board.N
    zobrist_hash_values = generate_unique_random_numbers(N)    
    return zobrist_hash_values

def hash_key_from_board(zobrist_values, board: SudokuBoard):
    """
    Function to generate a zobrist hash key from an input game state.
    @param zobrist_values a 2D numpy array containing the 64-bit values representing all possible (square, value) tuples
    @param board the state of the sudoku board to generate a hash key for
    @return a hash key uniquely representing the board state 
    """
    # hash key needs to be zero for empty board
    hash_key = np.uint64(0)

    # for each filled square in the board XOR the hash key with the zobrist value corresponding to that (square, value) tuple
    for index, square_value in enumerate(board.squares):
        print(index, square_value)
        # only update the hash key for non-empty squares
        if square_value != SudokuBoard.empty:
            # the new hash key value becomes the old value XOR'ed with the corresponding zobrist value
            hash_key = np.bitwise_xor(hash_key, zobrist_values[index, square_value - 1])

    return hash_key

def update_hash_key_on_move(zobrist_values, board: SudokuBoard, previous_hash_key, move: Move):
    """
    Function to generate a zobrist hash key from a game state with a known hash key and a newly played move.
    The old hash key will be updated to represent the newly played move. 
    This appoach avoids unnecessary repetition in calculating the hash keys of succeeding states.
    
    @param zobrist_values a 2D numpy array containing the 64-bit values representing all possible (square, value) tuples
    @param board the state of the sudoku board to generate a hash key for
    @param previous_hash_key the hash key representing the board state before the move is played
    @param move the move to be played to create a new board state
    @return a hash key uniquely representing the board state after the move has been played 
    """
    row, col, square_value = move.i, move.j, move.value
    index = row * board.N + col
    updated_hash_key = np.bitwise_xor(previous_hash_key, zobrist_values[index, square_value - 1])
    
    return updated_hash_key