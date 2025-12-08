
import random
from Backtracking import BacktrackingSolver

class SudokuGenerator:
    def __init__(self):
        self.solver = BacktrackingSolver()
        
    def generate_complete_board(self):
        board = [[0 for _ in range(9)] for _ in range(9)]
        
        # Fill diagonal 3x3 boxes first (they don't affect each other)
        self.fill_diagonal_boxes(board)
        
        # Fill remaining cells using backtracking
        self.solver.solve(board)
        
        return board
    
    def fill_diagonal_boxes(self, board):
        for box in range(0, 9, 3):
            self.fill_box(board, box, box)
    
    def fill_box(self, board, row_start, col_start):
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        
        idx = 0
        for i in range(3):
            for j in range(3):
                board[row_start + i][col_start + j] = numbers[idx]
                idx += 1
    
    def remove_numbers(self, board, difficulty):
        # Determine number of cells to remove based on difficulty
        if difficulty == 'easy':
            cells_to_remove = 35  # ~39% filled
        elif difficulty == 'medium':
            cells_to_remove = 45  # ~44% filled
        else:  # hard
            cells_to_remove = 55  # ~32% filled
        
        puzzle = [row[:] for row in board]
        
        # Get list of all cell positions
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)
        
        removed_count = 0
        attempts = 0
        max_attempts = len(cells) * 2
        
        for row, col in cells:
            if removed_count >= cells_to_remove:
                break
            
            if attempts >= max_attempts:
                break
                
            attempts += 1
            
            # Save current value
            backup = puzzle[row][col]
            puzzle[row][col] = 0
            
            # Check if puzzle still has unique solution
            if self.solver.has_unique_solution(puzzle):
                removed_count += 1
            else:
                # Restore value if multiple solutions exist
                puzzle[row][col] = backup
        
        return puzzle
    
    def generate_puzzle(self, difficulty='medium'):
        # Generate complete board
        complete_board = self.generate_complete_board()
        
        # Remove numbers to create puzzle
        puzzle = self.remove_numbers(complete_board, difficulty)
        
        return puzzle
    
    def generate_symmetric_puzzle(self, difficulty='medium'):
        complete_board = self.generate_complete_board()
        puzzle = [row[:] for row in complete_board]
        
        # Determine removal count
        if difficulty == 'easy':
            pairs_to_remove = 18
        elif difficulty == 'medium':
            pairs_to_remove = 23
        else:
            pairs_to_remove = 28
        
        # Generate symmetric pairs (center symmetry)
        pairs = []
        for i in range(9):
            for j in range(9):
                symmetric_i = 8 - i
                symmetric_j = 8 - j
                if (i, j) < (symmetric_i, symmetric_j):
                    pairs.append(((i, j), (symmetric_i, symmetric_j)))
        
        # Add center cell if exists (for 9x9 it's position (4,4))
        pairs.append(((4, 4), (4, 4)))
        
        random.shuffle(pairs)
        
        removed = 0
        for pair in pairs:
            if removed >= pairs_to_remove:
                break
            
            cell1, cell2 = pair
            
            # Save values
            val1 = puzzle[cell1[0]][cell1[1]]
            val2 = puzzle[cell2[0]][cell2[1]]
            
            # Remove both
            puzzle[cell1[0]][cell1[1]] = 0
            if cell1 != cell2:
                puzzle[cell2[0]][cell2[1]] = 0
            
            # Check unique solution
            if self.solver.has_unique_solution(puzzle):
                removed += 1
            else:
                # Restore
                puzzle[cell1[0]][cell1[1]] = val1
                if cell1 != cell2:
                    puzzle[cell2[0]][cell2[1]] = val2
        
        return puzzle