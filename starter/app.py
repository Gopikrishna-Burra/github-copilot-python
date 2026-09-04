from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hinted_cells': set(),
    'hints_used': 0,
}


def _validate_hint_board(board):
    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        return False
    for row in board:
        if not isinstance(row, list) or len(row) != sudoku_logic.SIZE:
            return False
        if any(type(value) is not int or not 0 <= value <= sudoku_logic.SIZE for value in row):
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    if 'difficulty' in request.args:
        difficulty = request.args.get('difficulty')
        try:
            puzzle, solution = sudoku_logic.generate_puzzle_for_difficulty(difficulty)
        except ValueError as error:
            return jsonify({'error': str(error)}), 400
    else:
        clues = int(request.args.get('clues', 35))
        puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['hinted_cells'] = set()
    CURRENT['hints_used'] = 0
    return jsonify({'puzzle': puzzle})


@app.route('/hint', methods=['POST'])
def request_hint():
    if CURRENT.get('puzzle') is None or CURRENT.get('solution') is None:
        return jsonify({'error': 'No game in progress'}), 400

    if not request.is_json:
        return jsonify({'error': 'Invalid JSON request'}), 400
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or set(data) != {'board'}:
        return jsonify({'error': 'Request must contain only board'}), 400

    board = data['board']
    if not _validate_hint_board(board):
        return jsonify({'error': 'Board must be a valid 9x9 grid'}), 400

    puzzle = CURRENT['puzzle']
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] != sudoku_logic.EMPTY and board[row][col] != puzzle[row][col]:
                return jsonify({'error': 'Original clues cannot be changed'}), 400

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            coordinate = (row, col)
            if (
                puzzle[row][col] == sudoku_logic.EMPTY
                and board[row][col] == sudoku_logic.EMPTY
                and coordinate not in CURRENT['hinted_cells']
            ):
                CURRENT['hinted_cells'].add(coordinate)
                CURRENT['hints_used'] += 1
                return jsonify({
                    'row': row,
                    'col': col,
                    'value': CURRENT['solution'][row][col],
                    'hintsUsed': CURRENT['hints_used'],
                })

    return jsonify({'error': 'No hint available'}), 400

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

if __name__ == '__main__':
    app.run(debug=True)