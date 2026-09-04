// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let timerInterval = null;
let timerStartedAt = null;
let elapsedSeconds = 0;

function formatElapsedTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  if (timerStartedAt !== null) {
    elapsedSeconds = Math.floor((Date.now() - timerStartedAt) / 1000);
  }
  document.getElementById('timer').textContent = formatElapsedTime(elapsedSeconds);
}

function resetTimer() {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  timerStartedAt = null;
  elapsedSeconds = 0;
  updateTimerDisplay();
}

function startTimer() {
  resetTimer();
  timerStartedAt = Date.now();
  updateTimerDisplay();
  timerInterval = setInterval(updateTimerDisplay, 1000);
}

function stopTimer() {
  if (timerStartedAt === null) return;
  updateTimerDisplay();
  timerStartedAt = null;
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.prefilled = 'false';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/[^1-9]/g, '').slice(0, 1);
        e.target.classList.remove('incorrect');
        validateBoard();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      inp.className = 'sudoku-cell';
      inp.removeAttribute('aria-invalid');
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className = 'sudoku-cell prefilled';
        inp.dataset.prefilled = 'true';
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.dataset.prefilled = 'false';
      }
    }
  }
}

function validateBoard() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = getBoardValues(inputs);
  const conflictingCells = new Set();

  for (let row = 0; row < SIZE; row++) {
    const indexes = Array.from({length: SIZE}, (_, col) => row * SIZE + col);
    markDuplicateCells(board[row], indexes, conflictingCells, inputs);
  }
  for (let col = 0; col < SIZE; col++) {
    const values = [];
    const indexes = [];
    for (let row = 0; row < SIZE; row++) {
      values.push(board[row][col]);
      indexes.push(row * SIZE + col);
    }
    markDuplicateCells(values, indexes, conflictingCells, inputs);
  }
  for (let boxRow = 0; boxRow < SIZE; boxRow += 3) {
    for (let boxCol = 0; boxCol < SIZE; boxCol += 3) {
      const values = [];
      const indexes = [];
      for (let row = boxRow; row < boxRow + 3; row++) {
        for (let col = boxCol; col < boxCol + 3; col++) {
          values.push(board[row][col]);
          indexes.push(row * SIZE + col);
        }
      }
      markDuplicateCells(values, indexes, conflictingCells, inputs);
    }
  }

  for (let idx = 0; idx < inputs.length; idx++) {
    const input = inputs[idx];
    if (input.disabled) continue;
    input.classList.toggle('invalid', conflictingCells.has(idx));
    if (conflictingCells.has(idx)) {
      input.setAttribute('aria-invalid', 'true');
    } else {
      input.removeAttribute('aria-invalid');
    }
  }
}

function markDuplicateCells(values, indexes, conflictingCells, inputs) {
  const locations = {};
  values.forEach((value, offset) => {
    if (value === 0) return;
    const idx = indexes[offset];
    if (!locations[value]) locations[value] = [];
    locations[value].push(idx);
  });
  Object.values(locations).forEach((duplicateIndexes) => {
    if (duplicateIndexes.length < 2) return;
    duplicateIndexes.forEach((idx) => {
      if (!inputs[idx].disabled) conflictingCells.add(idx);
    });
  });
}

function getBoardValues(inputs) {
  const board = [];
  for (let row = 0; row < SIZE; row++) {
    board[row] = [];
    for (let col = 0; col < SIZE; col++) {
      const value = inputs[row * SIZE + col].value;
      board[row][col] = value ? parseInt(value, 10) : 0;
    }
  }
  return board;
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  if (!res.ok || !data.puzzle) return;
  renderPuzzle(data.puzzle);
  startTimer();
  document.getElementById('message').innerText = '';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = getBoardValues(inputs);
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.classList.remove('incorrect');
    if (incorrect.has(idx)) inp.classList.add('incorrect');
  }
  const hasEmptyCells = board.some(row => row.includes(0));
  if (!hasEmptyCells && incorrect.size === 0) {
    stopTimer();
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  // initialize
  newGame();
});