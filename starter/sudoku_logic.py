import copy
import random

SIZE = 9
EMPTY = 0
DIFFICULTY_CLUES = {"easy": 45, "medium": 35, "hard": 30}

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def count_solutions(board, limit=2):
    """Count valid Sudoku solutions, stopping when limit is reached."""
    if limit <= 0:
        return 0

    working_board = deep_copy(board)
    if not _is_valid_partial_board(working_board):
        return 0

    def count_from_current_board():
        best_cell = None
        best_candidates = None

        for row in range(SIZE):
            for col in range(SIZE):
                if working_board[row][col] != EMPTY:
                    continue
                candidates = [
                    num
                    for num in range(1, SIZE + 1)
                    if is_safe(working_board, row, col, num)
                ]
                if not candidates:
                    return 0
                if best_candidates is None or len(candidates) < len(best_candidates):
                    best_cell = (row, col)
                    best_candidates = candidates
                    if len(candidates) == 1:
                        break
            if best_candidates is not None and len(best_candidates) == 1:
                break

        if best_cell is None:
            return 1

        row, col = best_cell
        solutions = 0
        for candidate in best_candidates:
            working_board[row][col] = candidate
            solutions += count_from_current_board()
            working_board[row][col] = EMPTY
            if solutions >= limit:
                return limit
        return solutions

    return count_from_current_board()

def _is_valid_partial_board(board):
    if len(board) != SIZE or any(len(row) != SIZE for row in board):
        return False

    for row in board:
        if any(cell not in range(0, SIZE + 1) for cell in row):
            return False

    for row in range(SIZE):
        values = [cell for cell in board[row] if cell != EMPTY]
        if len(values) != len(set(values)):
            return False
    for col in range(SIZE):
        values = [board[row][col] for row in range(SIZE) if board[row][col] != EMPTY]
        if len(values) != len(set(values)):
            return False
    for start_row in range(0, SIZE, 3):
        for start_col in range(0, SIZE, 3):
            values = [
                board[row][col]
                for row in range(start_row, start_row + 3)
                for col in range(start_col, start_col + 3)
                if board[row][col] != EMPTY
            ]
            if len(values) != len(set(values)):
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def remove_cells(board, clues):
    cells_to_remove = max(0, SIZE * SIZE - clues)
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)

    for row, col in cells:
        if cells_to_remove == 0:
            break
        original_value = board[row][col]
        if original_value == EMPTY:
            continue
        board[row][col] = EMPTY
        if count_solutions(board, limit=2) == 1:
            cells_to_remove -= 1
        else:
            board[row][col] = original_value

def generate_puzzle(clues=35):
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution

def generate_puzzle_for_difficulty(difficulty):
    try:
        clues = DIFFICULTY_CLUES[difficulty]
    except KeyError:
        raise ValueError(f"Invalid difficulty: {difficulty}") from None
    return generate_puzzle(clues=clues)
