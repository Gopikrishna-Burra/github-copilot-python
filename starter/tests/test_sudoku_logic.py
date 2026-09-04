from pathlib import Path
import random
import sys

import pytest


STARTER_DIRECTORY = Path(__file__).resolve().parents[1]
if str(STARTER_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(STARTER_DIRECTORY))

import sudoku_logic


SOLVED_BOARD = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]

UNIQUE_PUZZLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]


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


def test_complete_valid_board_has_one_solution():
    assert sudoku_logic.count_solutions(SOLVED_BOARD) == 1


def test_known_unique_puzzle_has_one_solution():
    assert sudoku_logic.count_solutions(UNIQUE_PUZZLE) == 1


def test_multiple_solution_puzzle_stops_at_limit_two():
    puzzle = sudoku_logic.create_empty_board()

    assert sudoku_logic.count_solutions(puzzle, limit=2) == 2


def test_invalid_puzzle_has_no_solutions():
    invalid = sudoku_logic.deep_copy(SOLVED_BOARD)
    invalid[0][1] = invalid[0][0]

    assert sudoku_logic.count_solutions(invalid) == 0


def test_count_solutions_does_not_mutate_input():
    puzzle = sudoku_logic.deep_copy(UNIQUE_PUZZLE)
    original = sudoku_logic.deep_copy(puzzle)

    sudoku_logic.count_solutions(puzzle)

    assert puzzle == original


@pytest.mark.parametrize('clues', [35, 40])
def test_generate_puzzle_has_requested_clues_and_matching_solution(clues):
    random.seed(12345)

    puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)

    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == clues
    assert sudoku_logic.count_solutions(puzzle, limit=2) == 1
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
