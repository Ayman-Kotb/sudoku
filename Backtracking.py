"""
Backtracking Algorithm for Sudoku
Used for validation and puzzle generation
"""

class BacktrackingSolver:
    solution = None
    def __init__(self):
        pass
    
    @staticmethod
    def is_valid_placement(board, row, col, num):
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
        # Check each filled cell
        for i in range(9):
            for j in range(9):
                if isinstance(board[i][j], type('a')) :
                    return False
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
    
    @staticmethod
    def find_empty_cell(board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return (i, j)
        return None
    
    def solve(self, board):
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
                    self.solution = [row[:] for row in board]  
                    return True
                
                # Backtrack if solution not found
                board[row][col] = 0
        
        # No valid number found, backtrack
        return False
    
    def count_solutions(self, board, limit=2):
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
        return self.count_solutions(board, limit=2) == 1
    
    # def get_possible_values(self, board, row, col):
    #     if board[row][col] != 0:
    #         return []
    #
    #     possible = []
    #     for num in range(1, 10):
    #         if self.is_valid_placement(board, row, col, num):
    #             possible.append(num)
    #
    #     return possible