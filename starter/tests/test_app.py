from pathlib import Path
import sys

import pytest


STARTER_DIRECTORY = Path(__file__).resolve().parents[1]
if str(STARTER_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(STARTER_DIRECTORY))

import app as app_module
import sudoku_logic


@pytest.fixture
def client():
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None
    app_module.CURRENT['hinted_cells'] = set()
    app_module.CURRENT['hints_used'] = 0
    app_module.app.config.update(TESTING=True)

    with app_module.app.test_client() as test_client:
        yield test_client

    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None
    app_module.CURRENT['hinted_cells'] = set()
    app_module.CURRENT['hints_used'] = 0


SOLUTION = [
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


def start_hint_game(empty_cells=((0, 2), (0, 3))):
    puzzle = sudoku_logic.deep_copy(SOLUTION)
    for row, col in empty_cells:
        puzzle[row][col] = sudoku_logic.EMPTY
    app_module.CURRENT['puzzle'] = puzzle
    app_module.CURRENT['solution'] = sudoku_logic.deep_copy(SOLUTION)
    app_module.CURRENT['hinted_cells'] = set()
    app_module.CURRENT['hints_used'] = 0
    return puzzle


def test_index_returns_sudoku_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data
    assert b'sudoku-board' in response.data
    assert b'id="message" role="status" aria-live="polite"' in response.data
    assert b'<span id="timer-label">Time</span>' in response.data
    assert b'<time id="timer"' in response.data
    assert b'aria-labelledby="timer-label"' in response.data
    assert b'datetime="PT0M0S"' in response.data
    assert b'id="score-entry"' in response.data
    assert b'id="player-name"' in response.data
    assert b'id="save-score"' in response.data
    assert b'class="leaderboard"' in response.data
    assert b'id="leaderboard-title"' in response.data
    assert b'id="leaderboard-list"' in response.data
    assert b'id="theme-toggle"' in response.data
    assert b'type="button"' in response.data
    assert b'aria-pressed="false"' in response.data
    assert b'Switch to Dark Mode' in response.data
    assert b'id="hint-button"' in response.data
    assert b'id="hints-used"' in response.data


def test_main_script_contains_hint_and_leaderboard_hint_count_support(client):
    script = (STARTER_DIRECTORY / 'static' / 'main.js').read_text()

    assert "fetch('/hint'" in script
    assert '.hinted' in script
    assert 'hintsUsed' in script
    assert 'sudokuLeaderboard' in script


def test_new_returns_default_puzzle_and_stores_game(client, monkeypatch):
    expected_puzzle = sudoku_logic.create_empty_board()
    expected_solution = sudoku_logic.create_empty_board()

    def fake_generate_puzzle(clues):
        assert clues == 35
        return expected_puzzle, expected_solution

    monkeypatch.setattr(app_module.sudoku_logic, 'generate_puzzle', fake_generate_puzzle)

    response = client.get('/new')

    assert response.status_code == 200
    assert response.get_json() == {'puzzle': expected_puzzle}
    assert app_module.CURRENT == {
        'puzzle': expected_puzzle,
        'solution': expected_solution,
        'hinted_cells': set(),
        'hints_used': 0,
    }


def test_new_preserves_clues_parameter(client, monkeypatch):
    expected_puzzle = sudoku_logic.create_empty_board()
    expected_solution = sudoku_logic.create_empty_board()

    def fake_generate_puzzle(clues):
        assert clues == 40
        return expected_puzzle, expected_solution

    monkeypatch.setattr(app_module.sudoku_logic, 'generate_puzzle', fake_generate_puzzle)

    response = client.get('/new?clues=40')

    assert response.status_code == 200
    assert response.get_json() == {'puzzle': expected_puzzle}


@pytest.mark.parametrize('difficulty', ['easy', 'medium', 'hard'])
def test_new_supports_difficulty_parameter(client, monkeypatch, difficulty):
    expected_puzzle = sudoku_logic.create_empty_board()
    expected_solution = sudoku_logic.create_empty_board()

    def fake_generate_puzzle_for_difficulty(value):
        assert value == difficulty
        return expected_puzzle, expected_solution

    monkeypatch.setattr(
        app_module.sudoku_logic,
        'generate_puzzle_for_difficulty',
        fake_generate_puzzle_for_difficulty,
    )

    response = client.get(f'/new?difficulty={difficulty}')

    assert response.status_code == 200
    assert response.get_json() == {'puzzle': expected_puzzle}
    assert app_module.CURRENT == {
        'puzzle': expected_puzzle,
        'solution': expected_solution,
        'hinted_cells': set(),
        'hints_used': 0,
    }


def test_new_difficulty_takes_precedence_over_clues(client, monkeypatch):
    expected_puzzle = sudoku_logic.create_empty_board()
    expected_solution = sudoku_logic.create_empty_board()

    def fake_generate_puzzle_for_difficulty(difficulty):
        assert difficulty == 'easy'
        return expected_puzzle, expected_solution

    def fail_generate_puzzle(clues):
        pytest.fail('clues generation should not be called when difficulty is provided')

    monkeypatch.setattr(
        app_module.sudoku_logic,
        'generate_puzzle_for_difficulty',
        fake_generate_puzzle_for_difficulty,
    )
    monkeypatch.setattr(app_module.sudoku_logic, 'generate_puzzle', fail_generate_puzzle)

    response = client.get('/new?difficulty=easy&clues=30')

    assert response.status_code == 200
    assert response.get_json() == {'puzzle': expected_puzzle}


def test_new_invalid_difficulty_returns_bad_request(client, monkeypatch):
    def fail_generate_puzzle_for_difficulty(difficulty):
        raise ValueError(f'Invalid difficulty: {difficulty}')

    monkeypatch.setattr(
        app_module.sudoku_logic,
        'generate_puzzle_for_difficulty',
        fail_generate_puzzle_for_difficulty,
    )

    response = client.get('/new?difficulty=expert')

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Invalid difficulty: expert'}


def test_hint_returns_one_correct_cell_and_increments_count(client):
    puzzle = start_hint_game()
    original_puzzle = sudoku_logic.deep_copy(puzzle)

    response = client.post('/hint', json={'board': puzzle})
    data = response.get_json()

    assert response.status_code == 200
    assert set(data) == {'row', 'col', 'value', 'hintsUsed'}
    assert (data['row'], data['col']) == (0, 2)
    assert data['value'] == SOLUTION[0][2]
    assert data['hintsUsed'] == 1
    assert app_module.CURRENT['hinted_cells'] == {(0, 2)}
    assert app_module.CURRENT['puzzle'] == original_puzzle


def test_second_hint_selects_a_different_empty_cell_and_increments_count(client):
    puzzle = start_hint_game()

    first_response = client.post('/hint', json={'board': puzzle})
    puzzle[first_response.get_json()['row']][first_response.get_json()['col']] = first_response.get_json()['value']
    second_response = client.post('/hint', json={'board': puzzle})

    assert second_response.status_code == 200
    assert (second_response.get_json()['row'], second_response.get_json()['col']) == (0, 3)
    assert second_response.get_json()['hintsUsed'] == 2


def test_hint_rejects_request_without_active_game(client):
    response = client.post('/hint', json={'board': sudoku_logic.create_empty_board()})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


@pytest.mark.parametrize('payload', [None, {}, {'board': []}, {'board': [[0] * 9] * 8}])
def test_hint_rejects_malformed_or_missing_board(client, payload):
    start_hint_game()
    if payload is None:
        response = client.post('/hint', data='not json', content_type='application/json')
    else:
        response = client.post('/hint', json=payload)

    assert response.status_code == 400


@pytest.mark.parametrize('value', [-1, 10, '0', None, 1.5, True])
def test_hint_rejects_invalid_board_values(client, value):
    board = start_hint_game()
    board[0][2] = value

    response = client.post('/hint', json={'board': board})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Board must be a valid 9x9 grid'}


def test_hint_rejects_changed_original_clue(client):
    board = sudoku_logic.deep_copy(start_hint_game())
    board[0][0] = 9

    response = client.post('/hint', json={'board': board})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Original clues cannot be changed'}


def test_hint_does_not_select_filled_editable_cell(client):
    board = start_hint_game()
    board[0][2] = SOLUTION[0][2]

    response = client.post('/hint', json={'board': board})

    assert response.status_code == 200
    assert (response.get_json()['row'], response.get_json()['col']) == (0, 3)


def test_hint_does_not_select_previously_hinted_cell(client):
    board = start_hint_game()
    first_response = client.post('/hint', json={'board': board})
    first_hint = first_response.get_json()
    board[first_hint['row']][first_hint['col']] = first_hint['value']

    response = client.post('/hint', json={'board': board})

    assert response.status_code == 200
    assert (response.get_json()['row'], response.get_json()['col']) != (
        first_hint['row'], first_hint['col']
    )


def test_hint_rejects_extra_request_fields(client):
    start_hint_game()

    response = client.post('/hint', json={'board': SOLUTION, 'row': 0})

    assert response.status_code == 400


def test_hint_reports_no_available_cell_for_full_board(client):
    start_hint_game(empty_cells=())

    response = client.post('/hint', json={'board': SOLUTION})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No hint available'}


def test_new_resets_hint_state_after_successful_generation(client, monkeypatch):
    expected_puzzle = sudoku_logic.create_empty_board()
    expected_solution = sudoku_logic.create_empty_board()
    app_module.CURRENT['hinted_cells'] = {(0, 2)}
    app_module.CURRENT['hints_used'] = 1

    monkeypatch.setattr(
        app_module.sudoku_logic,
        'generate_puzzle_for_difficulty',
        lambda difficulty: (expected_puzzle, expected_solution),
    )

    response = client.get('/new?difficulty=easy')

    assert response.status_code == 200
    assert app_module.CURRENT['hinted_cells'] == set()
    assert app_module.CURRENT['hints_used'] == 0


def test_failed_new_does_not_reset_existing_hint_state(client, monkeypatch):
    start_hint_game()
    app_module.CURRENT['hinted_cells'] = {(0, 2)}
    app_module.CURRENT['hints_used'] = 1

    monkeypatch.setattr(
        app_module.sudoku_logic,
        'generate_puzzle_for_difficulty',
        lambda difficulty: (_ for _ in ()).throw(ValueError('Invalid difficulty: expert')),
    )

    response = client.get('/new?difficulty=expert')

    assert response.status_code == 400
    assert app_module.CURRENT['hinted_cells'] == {(0, 2)}
    assert app_module.CURRENT['hints_used'] == 1


def test_check_without_game_returns_error(client):
    board = sudoku_logic.create_empty_board()

    response = client.post('/check', json={'board': board})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_check_complete_matching_board_returns_no_incorrect_cells(client):
    client.get('/new')
    solution = app_module.CURRENT['solution']

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': []}


def test_check_reports_changed_cell_as_incorrect(client):
    client.get('/new')
    solution = app_module.CURRENT['solution']
    board = sudoku_logic.deep_copy(solution)
    board[0][0] = (solution[0][0] % sudoku_logic.SIZE) + 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [[0, 0]]}


def test_check_reports_empty_cells_as_incorrect_legacy_behavior(client):
    client.get('/new')
    solution = app_module.CURRENT['solution']
    board = sudoku_logic.deep_copy(solution)
    board[0][0] = sudoku_logic.EMPTY

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [[0, 0]]}
