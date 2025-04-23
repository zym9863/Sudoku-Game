document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const sudokuBoard = document.getElementById('sudoku-board');
    const newGameBtn = document.getElementById('new-game');
    const checkSolutionBtn = document.getElementById('check-solution');
    const difficultySelect = document.getElementById('difficulty');
    const messageElement = document.getElementById('message');

    // Game variables
    let selectedCell = null;
    let board = [];
    let solution = [];
    let difficulty = 'easy';

    // Initialize the game
    initializeGame();

    // Event listeners
    newGameBtn.addEventListener('click', () => {
        difficulty = difficultySelect.value;
        initializeGame();
    });

    checkSolutionBtn.addEventListener('click', checkSolution);

    // Handle keyboard input
    document.addEventListener('keydown', handleKeyDown);

    // Initialize the game
    function initializeGame() {
        clearMessage();
        createEmptyBoard();
        generateSudoku();

        // Add loading effect
        sudokuBoard.style.opacity = '0.5';
        sudokuBoard.style.transform = 'scale(0.95)';

        setTimeout(() => {
            renderBoard();
            sudokuBoard.style.opacity = '1';
            sudokuBoard.style.transform = 'scale(1)';
        }, 300);
    }

    // Create an empty 9x9 board
    function createEmptyBoard() {
        board = Array(9).fill().map(() => Array(9).fill(0));
        solution = Array(9).fill().map(() => Array(9).fill(0));
    }

    // Generate a valid Sudoku puzzle
    function generateSudoku() {
        // First, generate a solved board
        generateSolvedBoard();

        // Then, remove numbers based on difficulty
        removeNumbers();
    }

    // Generate a solved Sudoku board
    function generateSolvedBoard() {
        // Clear the solution board
        solution = Array(9).fill().map(() => Array(9).fill(0));

        // Fill the diagonal 3x3 boxes first (these can be filled independently)
        fillDiagonalBoxes();

        // Solve the rest of the board
        solveSudoku(solution);

        // Copy the solution to the playing board
        board = solution.map(row => [...row]);
    }

    // Fill the diagonal 3x3 boxes
    function fillDiagonalBoxes() {
        for (let box = 0; box < 3; box++) {
            const values = shuffle([1, 2, 3, 4, 5, 6, 7, 8, 9]);
            for (let i = 0; i < 3; i++) {
                for (let j = 0; j < 3; j++) {
                    const row = box * 3 + i;
                    const col = box * 3 + j;
                    solution[row][col] = values[i * 3 + j];
                }
            }
        }
    }

    // Solve the Sudoku board using backtracking
    function solveSudoku(board) {
        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                // Skip cells that are already filled
                if (board[row][col] !== 0) continue;

                // Try each number 1-9
                const shuffledNumbers = shuffle([1, 2, 3, 4, 5, 6, 7, 8, 9]);
                for (const num of shuffledNumbers) {
                    if (isValidPlacement(board, row, col, num)) {
                        board[row][col] = num;

                        // Recursively try to solve the rest of the board
                        if (solveSudoku(board)) {
                            return true;
                        }

                        // If we couldn't solve the board with this number, backtrack
                        board[row][col] = 0;
                    }
                }

                // If we've tried all numbers and none work, this board is unsolvable
                return false;
            }
        }

        // If we've filled all cells, the board is solved
        return true;
    }

    // Check if a number can be placed at a specific position
    function isValidPlacement(board, row, col, num) {
        // Check row
        for (let i = 0; i < 9; i++) {
            if (board[row][i] === num) return false;
        }

        // Check column
        for (let i = 0; i < 9; i++) {
            if (board[i][col] === num) return false;
        }

        // Check 3x3 box
        const boxRow = Math.floor(row / 3) * 3;
        const boxCol = Math.floor(col / 3) * 3;
        for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 3; j++) {
                if (board[boxRow + i][boxCol + j] === num) return false;
            }
        }

        return true;
    }

    // Remove numbers based on difficulty
    function removeNumbers() {
        let cellsToRemove;

        switch (difficulty) {
            case 'easy':
                cellsToRemove = 40; // Leave ~41 clues
                break;
            case 'medium':
                cellsToRemove = 50; // Leave ~31 clues
                break;
            case 'hard':
                cellsToRemove = 60; // Leave ~21 clues
                break;
            default:
                cellsToRemove = 40;
        }

        // Create a list of all positions
        const positions = [];
        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                positions.push({ row, col });
            }
        }

        // Shuffle the positions
        shuffle(positions);

        // Remove numbers one by one, ensuring the puzzle remains solvable
        for (let i = 0; i < cellsToRemove; i++) {
            const { row, col } = positions[i];
            const temp = board[row][col];
            board[row][col] = 0;

            // Check if the puzzle still has a unique solution
            // For simplicity, we're skipping the uniqueness check here
            // In a more advanced implementation, you would verify that the puzzle has exactly one solution
        }
    }

    // Render the Sudoku board
    function renderBoard() {
        // Clear the board
        sudokuBoard.innerHTML = '';

        // Create cells with staggered animation
        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                const cell = document.createElement('div');
                cell.classList.add('cell');
                cell.dataset.row = row;
                cell.dataset.col = col;

                // Add staggered animation
                const delay = (row + col) * 20;
                cell.style.opacity = '0';
                cell.style.transform = 'scale(0.9)';

                if (board[row][col] !== 0) {
                    cell.textContent = board[row][col];
                    cell.classList.add('prefilled');
                } else {
                    cell.addEventListener('click', () => selectCell(cell, row, col));
                }

                sudokuBoard.appendChild(cell);

                // Trigger animation
                setTimeout(() => {
                    cell.style.opacity = '1';
                    cell.style.transform = 'scale(1)';
                }, delay);
            }
        }
    }

    // Select a cell
    function selectCell(cell, row, col) {
        // Deselect the previously selected cell
        if (selectedCell) {
            selectedCell.classList.remove('selected');
        }

        // Select the new cell
        selectedCell = cell;
        selectedCell.classList.add('selected');

        // Add subtle highlight effect
        cell.style.transform = 'scale(1.05)';
        setTimeout(() => {
            cell.style.transform = 'scale(1)';
        }, 150);
    }

    // Handle keyboard input
    function handleKeyDown(e) {
        if (!selectedCell) return;

        const row = parseInt(selectedCell.dataset.row);
        const col = parseInt(selectedCell.dataset.col);

        // Only allow input for cells that weren't prefilled
        if (board[row][col] !== 0 && selectedCell.classList.contains('prefilled')) return;

        if (e.key >= '1' && e.key <= '9') {
            // Input a number
            const num = parseInt(e.key);
            board[row][col] = num;
            selectedCell.textContent = num;
            selectedCell.classList.remove('error');

            // Check if this move creates any conflicts
            if (!isValidMove(row, col, num)) {
                selectedCell.classList.add('error');
            }
        } else if (e.key === 'Backspace' || e.key === 'Delete' || e.key === '0') {
            // Clear the cell
            board[row][col] = 0;
            selectedCell.textContent = '';
            selectedCell.classList.remove('error');
        }
    }

    // Check if a move is valid (doesn't create conflicts)
    function isValidMove(row, col, num) {
        // Create a copy of the board without the current cell's value
        const tempBoard = board.map(r => [...r]);
        tempBoard[row][col] = 0;

        return isValidPlacement(tempBoard, row, col, num);
    }

    // Check if the current board state is a valid solution
    function checkSolution() {
        // Check if the board is complete
        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                if (board[row][col] === 0) {
                    showMessage('请填完所有空格！', 'error-message');
                    return;
                }
            }
        }

        // Check if the solution is valid
        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                const num = board[row][col];

                // Create a copy of the board without the current cell's value
                const tempBoard = board.map(r => [...r]);
                tempBoard[row][col] = 0;

                if (!isValidPlacement(tempBoard, row, col, num)) {
                    showMessage('解答不正确，请检查！', 'error-message');
                    return;
                }
            }
        }

        // If we get here, the solution is valid
        showMessage('恭喜！你成功解决了这个数独！', 'success');
    }

    // Show a message
    function showMessage(text, className) {
        messageElement.textContent = text;
        messageElement.className = 'message ' + (className || '');

        // Add animation effect
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(-10px)';

        setTimeout(() => {
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
        }, 10);
    }

    // Clear the message
    function clearMessage() {
        messageElement.textContent = '';
        messageElement.className = 'message';
    }

    // Utility function to shuffle an array
    function shuffle(array) {
        const newArray = [...array];
        for (let i = newArray.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
        }
        return newArray;
    }
});
