import unittest
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
from team29_A1.sudokuai import SudokuAI
class Test(unittest.TestCase):
    def setUp(self):
        self.sudokuai = SudokuAI()

    def test_get_empty_squares(self):
        # Test for empty board
        empty_board = SudokuBoard()
        empty_squares = self.sudokuai.get_empty_squares(empty_board)
        self.assertEqual(empty_squares, [(i, j) for i in range(empty_board.board_height()) for j in range(empty_board.board_width())])

        # Test for 9x9 board with some filled squares
        filled_board = SudokuBoard()
        filled_board.put(0, 0, 1)
        filled_board.put(1, 1, 2)
        filled_board.put(2, 2, 3)
        filled_board.put(3, 3, 4)
        filled_squares = self.sudokuai.get_empty_squares(filled_board)
        self.assertEqual(filled_squares, [(i, j) for i in range(filled_board.board_height()) 
                                          for j in range(filled_board.board_width()) if (i, j) not in [(0, 0), (1, 1), (2, 2), (3, 3)]])
        
    def test_isinrow(self):
        # Test for empty board
        testboard = SudokuBoard(n=3, m=2)
        empty_squares = self.sudokuai.get_empty_squares(empty_board)
        self.assertEqual(empty_squares, [(i, j) for i in range(empty_board.board_height()) for j in range(empty_board.board_width())])

if __name__ == '__main__':
    unittest.main()
