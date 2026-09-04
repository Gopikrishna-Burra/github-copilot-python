from pathlib import Path
import random
import sys


STARTER_DIRECTORY = Path(__file__).resolve().parents[1]
if str(STARTER_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(STARTER_DIRECTORY))

import sudoku_logic


def is_valid_complete_board(board):
    expected = set(range(1, sudoku_logic.SIZE + 1))
    rows = all(set(row) == expected for row in board)
    columns = all(
        {board[row][column] for row in range(sudoku_logic.SIZE)} == expected
        for column in range(sudoku_logic.SIZE)
    )
    boxes = all(
        {
            board[row][column]
            for row in range(box_row, box_row + 3)
            for column in range(box_column, box_column + 3)
        }
        == expected
        for box_row in range(0, sudoku_logic.SIZE, 3)
        for box_column in range(0, sudoku_logic.SIZE, 3)
    )
    return rows and columns and boxes


def test_create_empty_board_returns_nine_by_nine_board():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_deep_copy_is_independent_from_original_board():
    original = sudoku_logic.create_empty_board()
    copied = sudoku_logic.deep_copy(original)

    copied[0][0] = 7

    assert original[0][0] == sudoku_logic.EMPTY
    assert copied[0][0] == 7


def test_is_safe_rejects_row_column_and_box_duplicates():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert not sudoku_logic.is_safe(board, 0, 1, 5)
    assert not sudoku_logic.is_safe(board, 1, 0, 5)
    assert not sudoku_logic.is_safe(board, 1, 1, 5)
    assert sudoku_logic.is_safe(board, 1, 1, 6)


def test_fill_board_produces_a_valid_complete_board():
    random.seed(12345)
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board)
    assert is_valid_complete_board(board)


def test_generate_puzzle_has_requested_clues_and_matching_solution():
    random.seed(12345)

    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35
    assert is_valid_complete_board(solution)
    assert all(
        puzzle[row][column] == sudoku_logic.EMPTY
        or puzzle[row][column] == solution[row][column]
        for row in range(sudoku_logic.SIZE)
        for column in range(sudoku_logic.SIZE)
    )


def test_generate_puzzle_returns_independent_puzzle_and_solution():
    random.seed(12345)

    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)
    original_solution_value = solution[0][0]
    puzzle[0][0] = 9 if original_solution_value != 9 else 8

    assert solution[0][0] == original_solution_value
