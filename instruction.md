# Copilot Instructions — Flask Sudoku Project

## Project Overview

This project is a Python Flask Sudoku web application being refactored from legacy code into a modular, maintainable, and user-friendly application.

The application should support:

* Sudoku puzzle generation
* Easy, Medium, and Hard difficulty levels
* Exactly one unique solution for every generated puzzle
* Locked prefilled cells
* Immediate validation of user entries
* Check Puzzle functionality
* Hint functionality
* Puzzle completion detection
* Game timer
* Top 10 leaderboard
* Local storage persistence
* Dark mode
* Responsive desktop and mobile layouts
* Accessible controls and readable UI

## General Development Principles

* Prefer clear, readable, maintainable Python and JavaScript.
* Follow modern Python practices and PEP 8 conventions.
* Use descriptive names for variables, functions, classes, and modules.
* Keep functions focused on a single responsibility.
* Avoid unnecessary duplication.
* Prefer modular and reusable components over large monolithic functions.
* Add comments where they clarify non-obvious logic, algorithms, or design decisions.
* Do not add comments that simply restate obvious code.
* Use consistent formatting throughout the project.
* Avoid unnecessary dependencies when the existing Python standard library or current project dependencies are sufficient.
* Preserve existing working functionality when refactoring unless the requirement explicitly calls for changing it.

## Architecture

Keep responsibilities separated:

* Flask routes should handle HTTP requests, responses, and application flow.
* Sudoku logic should remain independent from Flask and UI concerns.
* Front-end JavaScript should handle interactive game behavior and communication with Flask.
* HTML templates should focus on structure and semantic markup.
* CSS should handle presentation, responsive behavior, light/dark themes, and Sudoku grid styling.

Do not place large amounts of Sudoku-solving logic directly inside Flask route handlers.

## Sudoku Logic Requirements

Sudoku uses a 9x9 board with 3x3 subgrids.

The application must:

* Generate valid completed Sudoku boards.
* Generate puzzles by removing values from a valid solution.
* Guarantee that every generated puzzle has exactly one valid solution.
* Provide Easy, Medium, and Hard difficulty levels.
* Ensure difficulty changes the number of prefilled cells appropriately.
* Never modify or unlock original prefilled cells during gameplay.
* Keep generated solutions separate from the player's editable board.

When implementing solution counting or uniqueness validation, prioritize correctness over premature optimization.

Sudoku validation must correctly enforce:

* Row constraints
* Column constraints
* 3x3 subgrid constraints

## Flask Development

* Use appropriate HTTP methods for routes.
* Validate incoming request data.
* Handle missing or invalid request data gracefully.
* Return meaningful HTTP status codes and JSON responses for API endpoints.
* Avoid exposing unnecessary internal implementation details in error responses.
* Keep application state management clear and understandable.
* Avoid introducing unnecessary global mutable state when a better structure is practical.

## Front-End Development

* Keep JavaScript modular and readable.
* Avoid putting large inline JavaScript blocks inside HTML templates.
* Use semantic HTML where practical.
* Buttons and controls should have clear labels.
* Provide visual feedback for invalid entries and completed puzzles.
* Prefilled and hint-generated cells should be visually distinguishable where appropriate.
* Avoid layout shifts when styling the Sudoku grid.

## Responsive Design

The application must work cleanly on:

* Desktop screens
* Tablets
* Mobile phones

The Sudoku board should remain usable at smaller screen sizes without causing horizontal overflow.

Controls should remain readable and accessible across screen sizes.

## Light and Dark Modes

The application must support both light and dark modes.

* Text must remain readable in both modes.
* Buttons and controls must remain visible in both modes.
* Sudoku grid borders and cell states must remain distinguishable.
* Use CSS variables where practical to keep theme management consistent.

## Sudoku Grid Styling

The 9x9 board should clearly communicate the 3x3 Sudoku regions.

* Alternate styling between 3x3 regions.
* Maintain consistent cell dimensions.
* Keep borders visually clear.
* Do not introduce visible layout shifts when cells change state.
* Ensure invalid, hinted, selected, and prefilled cells can be distinguished.

## Game Features

### Hint

The Hint feature must:

* Fill one currently empty cell with the correct solution value.
* Never overwrite a player's existing value.
* Lock the newly filled cell.
* Update the appropriate hint count/state.
* Not make the puzzle invalid.

### Check

The Check feature must:

* Compare the player's current entries against the solution.
* Highlight incorrect entries.
* Leave correct entries unchanged.
* Handle incomplete boards without incorrectly marking empty cells as wrong.

### Completion

When the player correctly completes the puzzle:

* Detect successful completion.
* Stop the timer.
* Display a clear congratulatory message.
* Record the completion time.
* Update the Top 10 leaderboard when appropriate.

## Leaderboard and Local Storage

The Top 10 leaderboard should store:

* Player name
* Completion time
* Difficulty
* Number of hints used

Leaderboard data must persist between browser sessions using local storage.

Only the fastest 10 qualifying scores should be retained.

Leaderboard operations should handle missing, malformed, or empty local-storage data gracefully.

## Timer

The timer should:

* Start when a new puzzle begins.
* Track elapsed gameplay time.
* Stop when the puzzle is correctly completed.
* Reset for a new game.
* Display the elapsed time clearly.

The timer should not continue running after successful completion.

## Testing

Testing is an important part of the project.

Before refactoring existing code, establish a testing framework and confirm the baseline tests.

Whenever possible, add or update tests when implementing new functionality.

Tests should cover important behavior including:

* Sudoku board validity
* Sudoku solving
* Unique solution detection
* Difficulty levels
* Puzzle generation
* Locked cells
* Validation
* Hint behavior
* Check behavior
* Completion behavior
* Relevant Flask routes

After significant changes, run the test suite and fix regressions before continuing.

Do not remove or weaken tests simply to make the test suite pass.

## Error Handling

Use explicit and consistent error handling.

* Validate user input.
* Handle malformed requests gracefully.
* Avoid uncaught exceptions in normal user flows.
* Return useful errors from API endpoints.
* Do not hide genuine programming errors merely to make tests pass.

## Copilot Behavior

When assisting with this project:

1. First understand the existing code before making broad changes.
2. Explain significant architectural changes before applying them when practical.
3. Prefer incremental, focused changes over rewriting the entire project unnecessarily.
4. Do not modify unrelated files or functionality.
5. Preserve passing tests during refactoring.
6. When suggesting a dependency, explain why it is necessary.
7. When suggesting unfamiliar code or technology, explain how it works.
8. Point out potential trade-offs or risks in significant implementation decisions.
9. Do not assume a generated solution is correct; verify it through tests.
10. If a proposed change could affect multiple parts of the application, identify those areas before modifying them.

## Code Quality

The final application should be:

* Modular
* Readable
* Maintainable
* Testable
* Responsive
* Accessible
* Consistent
* Robust against invalid input

Correctness and maintainability are more important than minimizing the number of lines of code.
