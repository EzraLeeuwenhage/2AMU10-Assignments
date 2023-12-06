import unittest
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove, load_sudoku_from_text
from team29_A1.sudokuai import SudokuAI

class Test(unittest.TestCase):
    def setUp(self):
        self.sudokuai = SudokuAI()

    def test_get_valid_moves(self):
        # Test for an empty board
        empty_board = SudokuBoard()
        empty_game_state = GameState(empty_board, empty_board, [], [], [])
        valid_moves_empty = self.sudokuai.get_valid_moves(empty_game_state)
        self.assertEqual(valid_moves_empty, [
            Move(i, j, value) for i in range(empty_board.board_height())
                             for j in range(empty_board.board_width())
                             for value in range(1, empty_board.N + 1)
        ])

        # Test for a filled board with all moves considered taboo
        filled_board_text = "2 2\n1 2 3 4\n3 4 1 2\n2 3 4 1\n4 1 2 3"
        filled_board = load_sudoku_from_text(filled_board_text)
        taboo_moves=[
            TabooMove(0, 0, 1),
            TabooMove(1, 1, 2),
            TabooMove(2, 2, 3),
            TabooMove(3, 3, 4)
        ]
        filled_game_state = GameState(filled_board, filled_board, taboo_moves, [], [])
        valid_moves_filled = self.sudokuai.get_valid_moves(filled_game_state)
        self.assertEqual(valid_moves_filled, [])

        # Test for a partially filled board with some taboo moves
        partial_board_text = """ 
            2 2
            1   2   3   .
            3   4   1   2
            2   1   .   3
            .   3   .   1
        """
        partial_board = load_sudoku_from_text(partial_board_text)
        taboo_moves=[
            
        ]
        partial_game_state = GameState(partial_board, partial_board, taboo_moves, [], [])
        valid_moves_partial = self.sudokuai.get_valid_moves(partial_game_state)
        expected_valid_moves = [
            Move(0, 3, 4), Move(2, 2, 4), Move(3, 0, 4), Move(3, 2, 2), Move(3, 2, 4)
        ]
        self.assertEqual(valid_moves_partial, expected_valid_moves)


if __name__ == '__main__':
    unittest.main()
