"""
Arc Consistency Algorithm (AC-3) for Sudoku CSP
Implements arc consistency with visualization
"""

from collections import deque
from Backtracking import BacktrackingSolver

class ArcConsistencySolver:
    def __init__(self):
        self.backtracking_solver = BacktrackingSolver()
        self.arc_log = []  # Store steps for visualization
        
    def initialize_domains(self, board):
        """
        Initialize domains for each cell
        - Pre-filled cells have singleton domain
        - Empty cells have domain [1-9]
        
        Args:
            board: 9x9 Sudoku board
            
        Returns:
            Dictionary mapping (row, col) to list of possible values
        """
        domains = {}
        for i in range(9):
            for j in range(9):
                if board[i][j] != 0:
                    # Pre-filled cell has only one value in domain
                    domains[(i, j)] = [board[i][j]]
                else:
                    # Empty cell initially has all values 1-9
                    domains[(i, j)] = list(range(1, 10))
        return domains
    
    def get_neighbors(self, cell):
        """
        Get all cells that share a constraint with the given cell
        (same row, column, or 3x3 box)
        
        Args:
            cell: (row, col) tuple
            
        Returns:
            Set of neighbor cells
        """
        row, col = cell
        neighbors = set()
        
        # Add all cells in same row
        for j in range(9):
            if j != col:
                neighbors.add((row, j))
        
        # Add all cells in same column
        for i in range(9):
            if i != row:
                neighbors.add((i, col))
        
        # Add all cells in same 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i, j) != cell:
                    neighbors.add((i, j))
        
        return neighbors
    
    def create_arc_queue(self):
        """
        Create initial queue of all arcs in the CSP
        An arc is a directed edge between two variables with a constraint
        
        Returns:
            Queue of arcs as tuples (Xi, Xj)
        """
        arcs = deque()
        
        for i in range(9):
            for j in range(9):
                cell = (i, j)
                neighbors = self.get_neighbors(cell)
                # Add directed arcs from this cell to all neighbors
                for neighbor in neighbors:
                    arcs.append((cell, neighbor))
        
        return arcs
    
    def revise(self, domains, xi, xj):
        """
        Make arc (Xi, Xj) consistent
        Remove values from domain of Xi that have no consistent value in Xj
        
        Args:
            domains: Current domains
            xi: First variable (cell)
            xj: Second variable (cell)
            
        Returns:
            True if domain of Xi was revised, False otherwise
        """
        revised = False
        values_to_remove = []
        
        # For each value in Xi's domain
        for value_i in domains[xi]:
            # Check if there exists a consistent value in Xj's domain
            consistent_found = False
            
            for value_j in domains[xj]:
                # Values are consistent if they're different (Sudoku constraint)
                if value_i != value_j:
                    consistent_found = True
                    break
            
            # If no consistent value found, mark for removal
            if not consistent_found:
                values_to_remove.append(value_i)
                revised = True
        
        # Remove inconsistent values
        for value in values_to_remove:
            domains[xi].remove(value)
            self.arc_log.append(
                f"Removed {value} from cell {xi} (arc {xi} -> {xj})"
            )
        
        return revised
    
    def ac3(self, domains):
        """
        AC-3 Algorithm for arc consistency
        
        Args:
            domains: Initial domains for all variables
            
        Returns:
            True if consistent domains found, False if inconsistency detected
        """
        # Create queue of all arcs
        queue = self.create_arc_queue()
        
        self.arc_log.append("\n=== Starting AC-3 Algorithm ===\n")
        self.arc_log.append(f"Initial queue size: {len(queue)} arcs\n")
        
        iteration = 0
        
        # Process arcs until queue is empty
        while queue:
            iteration += 1
            xi, xj = queue.popleft()
            
            # Make arc consistent
            if self.revise(domains, xi, xj):
                # If domain becomes empty, no solution exists
                if len(domains[xi]) == 0:
                    self.arc_log.append(
                        f"\nIteration {iteration}: Domain of {xi} became empty - NO SOLUTION\n"
                    )
                    return False
                
                # Add arcs from neighbors of Xi back to queue
                # (except the arc from Xj)
                neighbors = self.get_neighbors(xi)
                for xk in neighbors:
                    if xk != xj:
                        queue.append((xk, xi))
                
                self.arc_log.append(
                    f"Iteration {iteration}: Revised {xi}, domain = {domains[xi]}"
                )
        
        self.arc_log.append(f"\n=== AC-3 Completed after {iteration} iterations ===\n")
        return True
    
    def assign_singleton_domains(self, board, domains):
        """
        Assign values from singleton domains to the board
        
        Args:
            board: Current board state
            domains: Current domains
            
        Returns:
            Number of cells assigned
        """
        assigned_count = 0
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0 and len(domains[(i, j)]) == 1:
                    board[i][j] = domains[(i, j)][0]
                    assigned_count += 1
                    self.arc_log.append(
                        f"Assigned {board[i][j]} to cell ({i}, {j})"
                    )
        return assigned_count
    
    def is_complete(self, board):
        """Check if board is completely filled"""
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return False
        return True
    
    def select_unassigned_variable(self, board, domains):
        """
        Select next variable to assign using MRV heuristic
        (Minimum Remaining Values - choose cell with smallest domain)
        
        Args:
            board: Current board
            domains: Current domains
            
        Returns:
            (row, col) of cell with smallest domain, or None if all assigned
        """
        min_domain_size = 10
        best_cell = None
        
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    domain_size = len(domains[(i, j)])
                    if domain_size < min_domain_size:
                        min_domain_size = domain_size
                        best_cell = (i, j)
        
        return best_cell
    
    def solve_with_backtracking(self, board, domains):
        """
        Solve remaining puzzle using backtracking with arc consistency
        
        Args:
            board: Current board state
            domains: Current domains
            
        Returns:
            True if solution found, False otherwise
        """
        # Check if complete
        if self.is_complete(board):
            return True
        
        # Select variable using MRV heuristic
        cell = self.select_unassigned_variable(board, domains)
        if cell is None:
            return True
        
        row, col = cell
        
        # Try each value in domain
        for value in domains[(row, col)][:]:  # Copy domain list
            if self.backtracking_solver.is_valid_placement(board, row, col, value):
                # Assign value
                board[row][col] = value
                
                # Save current domains
                saved_domains = {k: v[:] for k, v in domains.items()}
                domains[(row, col)] = [value]
                
                # Apply arc consistency
                if self.ac3(domains):
                    # Assign singleton domains
                    self.assign_singleton_domains(board, domains)
                    
                    # Recursively solve
                    if self.solve_with_backtracking(board, domains):
                        return True
                
                # Backtrack
                board[row][col] = 0
                domains.update({k: v[:] for k, v in saved_domains.items()})
        
        return False
    
    def solve(self, board):
        """
        Main solving method using Arc Consistency
        
        Args:
            board: 9x9 Sudoku board
            
        Returns:
            Solved board if solution found, None otherwise
        """
        # Create working copy
        solution = [row[:] for row in board]
        
        # Initialize domains
        domains = self.initialize_domains(solution)
        
        self.arc_log.append("=== Initial Board ===\n")
        self.arc_log.append(self.board_to_string(solution) + "\n")
        
        # Apply AC-3
        if not self.ac3(domains):
            return None
        
        # Assign singleton domains
        self.assign_singleton_domains(solution, domains)
        
        self.arc_log.append("\n=== After Initial AC-3 ===\n")
        self.arc_log.append(self.board_to_string(solution) + "\n")
        
        # If not complete, use backtracking with arc consistency
        if not self.is_complete(solution):
            self.arc_log.append("\n=== Using Backtracking + AC-3 ===\n")
            if not self.solve_with_backtracking(solution, domains):
                return None
        
        self.arc_log.append("\n=== Final Solution ===\n")
        self.arc_log.append(self.board_to_string(solution) + "\n")
        
        return solution
    
    def solve_with_visualization(self, board):
        """
        Solve and return visualization log
        
        Args:
            board: 9x9 Sudoku board
            
        Returns:
            (solution, arc_log_string) tuple
        """
        self.arc_log = []
        solution = self.solve(board)
        arc_tree = "\n".join(self.arc_log)
        return solution, arc_tree
    
    def board_to_string(self, board):
        """Convert board to readable string format"""
        result = []
        for i in range(9):
            if i % 3 == 0 and i != 0:
                result.append("------+-------+------")
            row_str = ""
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    row_str += "| "
                row_str += str(board[i][j]) if board[i][j] != 0 else "."
                row_str += " "
            result.append(row_str)
        return "\n".join(result)