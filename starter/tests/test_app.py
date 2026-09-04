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
