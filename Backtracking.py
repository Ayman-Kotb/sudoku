"""
Backtracking Algorithm for Sudoku
Used for validation and puzzle generation
"""

class BacktrackingSolver:
    def __init__(self):
        pass
    
    def is_valid_placement(self, board, row, col, num):
        """
        Check if placing num at board[row][col] is valid
        
        Args:
            board: 9x9 Sudoku board
            row: row index (0-8)
            col: column index (0-8)
            num: number to place (1-9)
            
        Returns:
            True if placement is valid, False otherwise
        """
        # Check row constraint
        for j in range(9):
            if j != col and board[row][j] == num:
                return False
        
        # Check column constraint
        for i in range(9):
            if i != row and board[i][col] == num:
                return False
        
        # Check 3x3 box constraint
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i != row or j != col) and board[i][j] == num:
                    return False
        
        return True
    
    def is_valid_board(self, board):
        """
        Check if the current board configuration is valid
        (no constraint violations)
        
        Args:
            board: 9x9 Sudoku board
            
        Returns:
            True if board is valid, False otherwise
        """
        # Check each filled cell
        for i in range(9):
            for j in range(9):
                if board[i][j] != 0:
                    num = board[i][j]
                    # Temporarily remove the number
                    board[i][j] = 0
                    # Check if it's valid
                    if not self.is_valid_placement(board, i, j, num):
                        board[i][j] = num  # Restore
                        return False
                    board[i][j] = num  # Restore
        return True
    
    def find_empty_cell(self, board):
        """
        Find the next empty cell in the board
        
        Args:
            board: 9x9 Sudoku board
            
        Returns:
            (row, col) tuple of empty cell, or None if board is full
        """
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return (i, j)
        return None
    
    def solve(self, board):
        """
        Solve Sudoku using backtracking algorithm
        
        Args:
            board: 9x9 Sudoku board (modified in place)
            
        Returns:
            True if solution found, False otherwise
        """
        # Find empty cell
        empty = self.find_empty_cell(board)
        
        # Base case: no empty cells means puzzle is solved
        if empty is None:
            return True
        
        row, col = empty
        
        # Try numbers 1-9
        for num in range(1, 10):
            if self.is_valid_placement(board, row, col, num):
                # Place the number
                board[row][col] = num
                
                # Recursively try to solve
                if self.solve(board):
                    return True
                
                # Backtrack if solution not found
                board[row][col] = 0
        
        # No valid number found, backtrack
        return False
    
    def count_solutions(self, board, limit=2):
        """
        Count the number of solutions for a given board
        Used to ensure puzzle has unique solution
        
        Args:
            board: 9x9 Sudoku board
            limit: stop counting after this many solutions
            
        Returns:
            Number of solutions (capped at limit)
        """
        def count_helper(board, count):
            if count[0] >= limit:
                return
            
            empty = self.find_empty_cell(board)
            if empty is None:
                count[0] += 1
                return
            
            row, col = empty
            for num in range(1, 10):
                if self.is_valid_placement(board, row, col, num):
                    board[row][col] = num
                    count_helper(board, count)
                    board[row][col] = 0
        
        # Create a copy to avoid modifying original
        board_copy = [row[:] for row in board]
        count = [0]
        count_helper(board_copy, count)
        return count[0]
    
    def has_unique_solution(self, board):
        """
        Check if puzzle has exactly one solution
        
        Args:
            board: 9x9 Sudoku board
            
        Returns:
            True if unique solution exists, False otherwise
        """
        return self.count_solutions(board, limit=2) == 1
    
    def get_possible_values(self, board, row, col):
        """
        Get all possible values for a cell
        
        Args:
            board: 9x9 Sudoku board
            row: row index
            col: column index
            
        Returns:
            List of possible values (1-9)
        """
        if board[row][col] != 0:
            return []
        
        possible = []
        for num in range(1, 10):
            if self.is_valid_placement(board, row, col, num):
                possible.append(num)
        
        return possible