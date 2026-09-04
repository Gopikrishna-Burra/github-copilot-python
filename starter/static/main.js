// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_STORAGE_KEY = 'sudokuLeaderboard';
const THEME_STORAGE_KEY = 'sudokuTheme';
const SUPPORTED_DIFFICULTIES = new Set(['easy', 'medium', 'hard']);
let puzzle = [];
let timerInterval = null;
let timerStartedAt = null;
let elapsedSeconds = 0;
let completedTimeSeconds = null;
let currentGameDifficulty = 'medium';
let scoreSubmitted = false;

function getStoredTheme() {
  try {
    const theme = localStorage.getItem(THEME_STORAGE_KEY);
    return theme === 'dark' || theme === 'light' ? theme : 'light';
  } catch (error) {
    return 'light';
  }
}

function applyTheme(theme) {
  const selectedTheme = theme === 'dark' ? 'dark' : 'light';
  document.documentElement.dataset.theme = selectedTheme;
  updateThemeToggle();
  try {
    localStorage.setItem(THEME_STORAGE_KEY, selectedTheme);
  } catch (error) {
    // Theme changes continue to work for the current page if storage fails.
  }
}

function updateThemeToggle() {
  const toggle = document.getElementById('theme-toggle');
  if (!toggle) return;
  const isDark = document.documentElement.dataset.theme === 'dark';
  toggle.setAttribute('aria-pressed', String(isDark));
  toggle.textContent = isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode';
}

function toggleTheme() {
  const nextTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  applyTheme(nextTheme);
}

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

function loadLeaderboard() {
  try {
    const storedScores = localStorage.getItem(LEADERBOARD_STORAGE_KEY);
    if (storedScores === null) return [];

    const scores = JSON.parse(storedScores);
    if (!Array.isArray(scores)) return [];
    return scores.filter((score) => {
      return score
        && typeof score.name === 'string'
        && score.name.trim().length > 0
        && score.name.trim().length <= 30
        && typeof score.timeSeconds === 'number'
        && Number.isFinite(score.timeSeconds)
        && score.timeSeconds >= 0
        && SUPPORTED_DIFFICULTIES.has(score.difficulty);
    }).map((score) => ({
      name: score.name.trim(),
      timeSeconds: score.timeSeconds,
      difficulty: score.difficulty,
    }));
  } catch (error) {
    return [];
  }
}

function saveLeaderboard(scores) {
  try {
    localStorage.setItem(LEADERBOARD_STORAGE_KEY, JSON.stringify(scores));
    return true;
  } catch (error) {
    return false;
  }
}

function sortLeaderboard(scores) {
  return scores
    .map((score, index) => ({score, index}))
    .sort((left, right) => left.score.timeSeconds - right.score.timeSeconds || left.index - right.index)
    .map(({score}) => score);
}

function addLeaderboardScore(score) {
  const scores = sortLeaderboard([...loadLeaderboard(), score]).slice(0, 10);
  saveLeaderboard(scores);
  renderLeaderboard();
}

function renderLeaderboard() {
  const list = document.getElementById('leaderboard-list');
  list.textContent = '';
  const scores = sortLeaderboard(loadLeaderboard()).slice(0, 10);
  if (scores.length === 0) {
    const emptyItem = document.createElement('li');
    emptyItem.textContent = 'No scores yet.';
    list.appendChild(emptyItem);
    return;
  }

  scores.forEach((score, index) => {
    const item = document.createElement('li');
    item.textContent = `${index + 1}. ${score.name} - ${formatElapsedTime(score.timeSeconds)} - ${score.difficulty}`;
    list.appendChild(item);
  });
}

function showScoreEntry() {
  const scoreEntry = document.getElementById('score-entry');
  const playerName = document.getElementById('player-name');
  scoreEntry.hidden = false;
  playerName.focus();
}

function hideScoreEntry() {
  const scoreEntry = document.getElementById('score-entry');
  const playerName = document.getElementById('player-name');
  const scoreError = document.getElementById('score-error');
  scoreEntry.hidden = true;
  playerName.value = '';
  playerName.removeAttribute('aria-invalid');
  scoreError.textContent = '';
}

function handleScoreSubmission(event) {
  event.preventDefault();
  if (scoreSubmitted || completedTimeSeconds === null) return;

  const playerName = document.getElementById('player-name');
  const scoreError = document.getElementById('score-error');
  const name = playerName.value.trim();
  if (!name || name.length > 30) {
    playerName.setAttribute('aria-invalid', 'true');
    scoreError.textContent = 'Please enter a name of 1 to 30 characters.';
    playerName.focus();
    return;
  }

  addLeaderboardScore({
    name,
    timeSeconds: completedTimeSeconds,
    difficulty: currentGameDifficulty,
  });
  scoreSubmitted = true;
  document.getElementById('save-score').disabled = true;
  hideScoreEntry();
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      const boxRow = Math.floor(i / 3);
      const boxCol = Math.floor(j / 3);
      const boxClass = (boxRow + boxCol) % 2 === 0 ? 'box-light' : 'box-dark';
      input.type = 'text';
      input.maxLength = 1;
      input.className = `sudoku-cell ${boxClass}`;
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
      const boxRow = Math.floor(i / 3);
      const boxCol = Math.floor(j / 3);
      const boxClass = (boxRow + boxCol) % 2 === 0 ? 'box-light' : 'box-dark';
      inp.className = `sudoku-cell ${boxClass}`;
      inp.removeAttribute('aria-invalid');
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className = `sudoku-cell ${boxClass} prefilled`;
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
  currentGameDifficulty = difficulty;
  completedTimeSeconds = null;
  scoreSubmitted = false;
  document.getElementById('save-score').disabled = false;
  hideScoreEntry();
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
    msg.className = 'message-error';
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
    if (completedTimeSeconds === null) {
      stopTimer();
      completedTimeSeconds = elapsedSeconds;
      showScoreEntry();
    }
    msg.className = 'message-success';
    msg.innerText = 'Congratulations! You solved it!';
  } else {
    msg.className = 'message-error';
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  applyTheme(getStoredTheme());
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('save-score').addEventListener('click', handleScoreSubmission);
  renderLeaderboard();
  // initialize
  newGame();
});