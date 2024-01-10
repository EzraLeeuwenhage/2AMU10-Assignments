import numpy as np
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard
import hashlib

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
    
    One extra value is added for hashing the current game info (score and current player), such that a unique game state is represented.

    @param initialboard: initial_board attribute of the game state object
    @return 2D numpy array of length N^2 with each index containing N
    """
    N = initial_board.N
    zobrist_hash_values = generate_unique_random_numbers(N)

    return zobrist_hash_values

def hash_game_info(current_score: list[int], current_player):
    """
    Hashes the game state information, including the score and current player.

    @param current_score (list[int]): A list containing the scores of the players.
    @param current_player The identifier of the current player.

    @returns np.hash_uint64 A 64-bit unsigned integer representing the hash of the game state information (score and current player).
    """
    # convert the list of scores to a string, with scores separated by spaces
    score_str = ' '.join(map(str, current_score))
    game_info_str = f"{score_str} {current_player}"
    
    # add hashed tuple of game score and current player as a single hash value 
    # take the first 8 bytes of the hash value (since we need 64 bit values for XOR'ing)
    # convert the resulting integer to a uint64 value using numpy
    hashed_game_info = hashlib.sha256(game_info_str.encode()) # 256 bit value
    hash_int = int.from_bytes(hashed_game_info.digest()[:8], byteorder='big') # int value
    hash_uint64 = np.uint64(hash_int) # uint64 value

    return hash_uint64

def hash_key_from_gamestate(zobrist_values, game_state: GameState):
    """
    Function to generate a zobrist hash key from an input game state.
    @param zobrist_values a 2D numpy array containing the 64-bit values representing all possible (square, value) tuples
    @param game_state the state of the game to generate a hash key for
    @return a hash key uniquely representing the game state, i.e. the board state plus the current score and current player
    """
    # hash key needs to be zero for empty board
    hash_key = np.uint64(0)

    # for each filled square in the board XOR the hash key with the zobrist value corresponding to that (square, value) tuple
    for index, square_value in enumerate(game_state.board.squares):
        # only update the hash key for non-empty squares
        if square_value != SudokuBoard.empty:
            # the new hash key value becomes the old value XOR'ed with the corresponding zobrist value
            hash_key = np.bitwise_xor(hash_key, zobrist_values[index, square_value - 1])

    # hash the game info (current score and current player)
    current_player = game_state.current_player()
    game_info_hash = hash_game_info(game_state.scores, current_player)
    # XOR the hash key representing the board with the game info (current score and current player)
    hash_key = np.bitwise_xor(hash_key, game_info_hash)

    return hash_key

# FIXME: probably this function has become redundant since the computation time is no longer more efficient than computing from scratch
def update_hash_key_on_move(zobrist_values, board: SudokuBoard, old_gamestate_hash, move: Move):
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
    # to get the updated hash key after a move is played we need to first retreive the hashkey of the old board state (XOR with game info)

    # then we XOR the old board state hash with the played move to get the hash for the new board state as below
    row, col, square_value = move.i, move.j, move.value
    index = row * board.N + col
    updated_hash_key = np.bitwise_xor(old_gamestate_hash, zobrist_values[index, square_value - 1])

    # finally we XOR the new board state hash with the new game state info (new score and current player)
    
    return updated_hash_key