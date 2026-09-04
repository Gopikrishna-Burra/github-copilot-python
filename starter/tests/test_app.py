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
    app_module.app.config.update(TESTING=True)

    with app_module.app.test_client() as test_client:
        yield test_client

    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None


def test_index_returns_sudoku_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data
    assert b'sudoku-board' in response.data
    assert b'id="message" role="status" aria-live="polite"' in response.data


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
