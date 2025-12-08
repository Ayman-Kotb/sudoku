from collections import deque
from Backtracking import BacktrackingSolver

class ArcConsistencySolver:
    def __init__(self):
        self.backtracking_solver = BacktrackingSolver()
        self.arc_log = []  # Store steps for visualization
        
    def initialize_domains(self, board):
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
        assigned_cells = []
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0 and len(domains[(i, j)]) == 1:
                    val = domains[(i, j)][0]
                    board[i][j] = val
                    domains[(i, j)] = [val]
                    assigned_cells.append((i, j))
                    self.arc_log.append(f"Assigned {val} to cell ({i}, {j})")
        return assigned_cells
    
    def is_complete(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return False
        return True
    
    def select_unassigned_variable(self, board, domains):
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
        if self.is_complete(board):
            return True

        cell = self.select_unassigned_variable(board, domains)
        if cell is None:
            return True

        row, col = cell

        for value in domains[(row, col)][:]:
            if self.backtracking_solver.is_valid_placement(board, row, col, value):
                board[row][col] = value

                saved_domains = {k: v[:] for k, v in domains.items()}
                domains[(row, col)] = [value]

                if self.ac3(domains):
                    assigned_cells = self.assign_singleton_domains(board, domains)

                    if self.solve_with_backtracking(board, domains):
                        return True

                    # Backtrack: revert board assignments done in this branch
                    for (ai, aj) in assigned_cells:
                        board[ai][aj] = 0

                # revert the chosen cell and domains
                board[row][col] = 0
                domains.update({k: v[:] for k, v in saved_domains.items()})

        return False

    def solve(self, board):
        solution = [row[:] for row in board]
        domains = self.initialize_domains(solution)

        self.arc_log.append("=== Initial Board ===\n")
        self.arc_log.append(self.board_to_string(solution) + "\n")

        while True:
            if not self.ac3(domains):
                return None

            assigned_cells = self.assign_singleton_domains(solution, domains)
            self.arc_log.append(f"Assigned {len(assigned_cells)} singletons in this pass\n")
            if len(assigned_cells) == 0:
                break

        self.arc_log.append("\n=== After Initial AC-3 ===\n")
        self.arc_log.append(self.board_to_string(solution) + "\n")

        if not self.is_complete(solution):
            self.arc_log.append("\n=== Using Backtracking + AC-3 ===\n")
            if not self.solve_with_backtracking(solution, domains):
                return None

        self.arc_log.append("\n=== Final Solution ===\n")
        self.arc_log.append(self.board_to_string(solution) + "\n")

        return solution
    
    def solve_with_visualization(self, board):
        self.arc_log = []
        solution = self.solve(board)
        arc_tree = "\n".join(self.arc_log)
        return solution, arc_tree
    
    def board_to_string(self, board):
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