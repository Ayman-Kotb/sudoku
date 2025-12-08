
import tkinter as tk
from tkinter import ttk, messagebox
import time
from Backtracking import BacktrackingSolver
from ArcConsistency import ArcConsistencySolver
from SudokuGenerator import SudokuGenerator

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver - CSP with Arc Consistency")
        self.root.geometry("855x750")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize solvers
        self.backtracking_solver = BacktrackingSolver()
        self.arc_solver = ArcConsistencySolver()
        self.generator = SudokuGenerator()
        
        # Game state
        self.previousBoard = [[0 for _ in range(9)] for _ in range(9)]
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.initial_board = [[0 for _ in range(9)] for _ in range(9)]
        self.cells = {}
        self.mode = tk.StringVar(value="mode1")
        self.difficulty = tk.StringVar(value="easy")
        self.mistakes = 0
        self.start_time = None
        self.timer_running = False

        self.setup_ui()
        
    def setup_ui(self):
        """Setup the complete user interface"""
        # Title
        title_frame = tk.Frame(self.root, bg='#f0f0f0')
        title_frame.pack(pady=5)
        
        title_label = tk.Label(title_frame, text="Sudoku Solver - CSP with Arc Consistency",
                              font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='#2C3E50')
        title_label.pack()
        
        # Main container
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(pady=5, padx=20, fill='both', expand=True)
        
        # Left panel - Sudoku board
        left_panel = tk.Frame(main_container, bg='#f0f0f0')
        left_panel.grid(row=0, column=0, padx=20, sticky='n')
        
        self.create_board(left_panel)
        
        # Right panel - Controls (with scrollbar)
        right_panel = tk.Frame(main_container, bg='#E8F0F8', width=300)
        right_panel.grid(row=0, column=1, padx=10, sticky='nsew')
        right_panel.grid_propagate(False)
        
        # Configure grid weights for resizing
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        self.create_controls(right_panel)
        
    def create_board(self, parent):
        """Create the 9x9 Sudoku grid"""
        # Info bar above board
        info_frame = tk.Frame(parent, bg='#f0f0f0')
        info_frame.pack(pady=(0, 10), fill='x')
        
        self.difficulty_label = tk.Label(info_frame, text="Difficulty: Easy",
                                        font=('Arial', 11, 'bold'), bg='#f0f0f0', fg='#333')
        self.difficulty_label.pack(side='left')

        # Sudoku board
        board_frame = tk.Frame(parent, bg='#4A90E2', bd=3)
        board_frame.pack()

        # Create 9x9 grid
        for i in range(9):
            for j in range(9):
                # Calculate border width for 3x3 boxes
                if i % 3 == 0 and i != 0:
                    pady_top = 2
                else:
                    pady_top = 0
                if j % 3 == 0 and j != 0:
                    padx_left = 2
                else:
                    padx_left = 0

                cell_frame = tk.Frame(board_frame, bg='#4A90E2')
                cell_frame.grid(row=i, column=j, padx=(padx_left, 0),
                               pady=(pady_top, 0))

                cell = tk.Entry(cell_frame, width=3, font=('Arial', 20, 'bold'),
                              justify='center', bd=1, relief='solid',
                              bg='#E8F4F8', fg='#2C3E50')
                cell.grid(row=0, column=0)
                cell.config(state='normal')

                # Bind events for interactive mode
                cell.bind('<FocusIn>', lambda e, r=i, c=j: self.on_cell_focus(r, c))
                cell.bind('<Key>', lambda e, r=i, c=j: self.on_key_press(e, r, c))

                self.cells[(i, j)] = cell

        # Status bar below board
        status_frame = tk.Frame(parent, bg='#f0f0f0')
        status_frame.pack(pady=(10, 5), fill='x')

        # Mistakes section
        mistakes_frame = tk.Frame(status_frame, bg='#f0f0f0')
        mistakes_frame.pack(side='left')

        tk.Label(mistakes_frame, text="Mistakes:", font=('Arial', 10),
                bg='#f0f0f0', fg='#666').pack(side='left')
        self.mistakes_label = tk.Label(mistakes_frame, text="0/3",
                                       font=('Arial', 10, 'bold'), bg='#f0f0f0',
                                       fg='#E74C3C')
        self.mistakes_label.pack(side='left', padx=5)

        # Timer section
        timer_frame = tk.Frame(status_frame, bg='#f0f0f0')
        timer_frame.pack(side='right')

        tk.Label(timer_frame, text="Time:", font=('Arial', 10),
                bg='#f0f0f0', fg='#666').pack(side='left', padx=5)
        self.timer_label = tk.Label(timer_frame, text="00:00",
                                   font=('Arial', 10, 'bold'), bg='#f0f0f0',
                                   fg='#27AE60')
        self.timer_label.pack(side='left')

        # Statistics panel below board
        stats_frame = tk.LabelFrame(parent, text="Puzzle Statistics",
                                   font=('Arial', 11, 'bold'),
                                   bg='#f0f0f0', fg='#2C3E50', padx=10, pady=10)
        stats_frame.pack(pady=(10, 0), fill='x')

        # Empty cells counter
        self.empty_cells_label = tk.Label(stats_frame, text="Empty Cells: 0",
                                         font=('Arial', 9), bg='#f0f0f0', fg='#555')
        self.empty_cells_label.pack(anchor='w', pady=2)

        # Pre-filled cells counter
        self.filled_cells_label = tk.Label(stats_frame, text="Pre-filled: 0",
                                          font=('Arial', 9), bg='#f0f0f0', fg='#555')
        self.filled_cells_label.pack(anchor='w', pady=2)

        # Solve time display
        self.solve_time_label = tk.Label(stats_frame, text="Last Solve: -",
                                        font=('Arial', 9), bg='#f0f0f0', fg='#555')
        self.solve_time_label.pack(anchor='w', pady=2)

    def create_controls(self, parent):
        """Create control buttons and options"""
        # Create scrollable frame for controls
        canvas = tk.Canvas(parent, bg='#E8F0F8', highlightthickness=0)
        scrollable_frame = tk.Frame(canvas, bg='#E8F0F8')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Mode selection
        mode_frame = tk.LabelFrame(scrollable_frame, text="Mode Selection",
                                   font=('Arial', 12, 'bold'),
                                   bg='#E8F0F8', padx=10, pady=10, fg='#2C3E50')
        mode_frame.pack(fill='x', pady=5, padx=5)

        tk.Radiobutton(mode_frame, text="Mode 1: AI Auto Solve",
                      variable=self.mode, value="mode1",
                      font=('Arial', 10), bg='#E8F0F8', fg='#2C3E50',
                      command=self.on_mode_change).pack(anchor='w')

        tk.Radiobutton(mode_frame, text="Mode 2: Input & Solve",
                      variable=self.mode, value="mode2",
                      font=('Arial', 10), bg='#E8F0F8', fg='#2C3E50',
                      command=self.on_mode_change).pack(anchor='w')

        tk.Radiobutton(mode_frame, text="Mode 3: Interactive Play",
                      variable=self.mode, value="mode3",
                      font=('Arial', 10), bg='#E8F0F8', fg='#2C3E50',
                      command=self.on_mode_change).pack(anchor='w')

        # Difficulty selection (for Mode 1 and 3)
        diff_frame = tk.LabelFrame(scrollable_frame, text="Difficulty",
                                   font=('Arial', 12, 'bold'),
                                   bg='#E8F0F8', padx=10, pady=10, fg='#2C3E50')
        diff_frame.pack(fill='x', pady=5, padx=5)

        tk.Radiobutton(diff_frame, text="Easy",
                      variable=self.difficulty, value="easy",
                      font=('Arial', 10), bg='#E8F0F8', fg='#2C3E50').pack(anchor='w')

        tk.Radiobutton(diff_frame, text="Medium",
                      variable=self.difficulty, value="medium",
                      font=('Arial', 10), bg='#E8F0F8', fg='#2C3E50').pack(anchor='w')

        tk.Radiobutton(diff_frame, text="Hard",
                      variable=self.difficulty, value="hard",
                      font=('Arial', 10), bg='#E8F0F8', fg='#2C3E50').pack(anchor='w')

        # Action buttons
        button_frame = tk.Frame(scrollable_frame, bg='#E8F0F8')
        button_frame.pack(fill='x', pady=10, padx=5)

        # New Game button (hidden in mode 2)
        self.new_game_btn = tk.Button(button_frame, text="New Game",
                                      font=('Arial', 12, 'bold'),
                                      bg='#4A90E2', fg='white',
                                      command=self.new_game, padx=20, pady=10,
                                      cursor='hand2')
        self.new_game_btn.pack(fill='x', pady=5)

        # Get previous game button
        self.prev_game_btn = tk.Button(button_frame, text="Get Previous Game",
                                      font=('Arial', 12, 'bold'),
                                      bg='#4A90E2', fg='white',
                                      command=self.getPreviousGame, padx=20, pady=10,
                                      cursor='hand2')
        self.prev_game_btn.pack(fill='x', pady=5)

        self.solve_btn = tk.Button(button_frame, text="Solve with Arc Consistency",
                                   font=('Arial', 12, 'bold'),
                                   bg='#4A90E2', fg='white',
                                   command=self.solve_puzzle, padx=20, pady=10,
                                   cursor='hand2')
        self.solve_btn.pack(fill='x', pady=5)

        self.solve_btn_using_normal_backtracking = tk.Button(button_frame, text="Solve with Backtracking",
                                   font=('Arial', 12, 'bold'),
                                   bg='#4A90E2', fg='white',
                                   command=self.solve_puzzle_using_backtrack, padx=20, pady=10,
                                   cursor='hand2')
        self.solve_btn_using_normal_backtracking.pack(fill='x', pady=5)

        self.clear_btn = tk.Button(button_frame, text="Clear Board",
                                   font=('Arial', 12, 'bold'),
                                   bg='#4A90E2', fg='white',
                                   command=self.clear_board, padx=20, pady=10,
                                   cursor='hand2')
        self.clear_btn.pack(fill='x', pady=5)

        self.validate_btn = tk.Button(button_frame, text="Validate Input",
                                      font=('Arial', 12, 'bold'),
                                      bg='#4A90E2', fg='white',
                                      command=self.validate_input, padx=20, pady=10,
                                      cursor='hand2')
        self.validate_btn.pack(fill='x', pady=5)

        self.show_arc_btn = tk.Button(button_frame, text="Show Arc Consistency Tree",
                                      font=('Arial', 12, 'bold'),
                                      bg='#4A90E2', fg='white',
                                      command=self.show_arc_tree, padx=20, pady=10,
                                      cursor='hand2')
        self.show_arc_btn.pack(fill='x', pady=5)

        # Status label
        self.status_label = tk.Label(scrollable_frame, text="Ready",
                                    font=('Arial', 10, 'italic'),
                                    bg='#E8F0F8', fg='#666')
        self.status_label.pack(pady=10)

        # Pack canvas and scrollbar
        canvas.pack(side="right", fill="both", expand=True)

    def on_mode_change(self):
        """Handle mode change"""
        mode = self.mode.get()

        self.timer_running = False
        self.start_time = None
        self.timer_label.config(text="00:00")

        # Reset mistakes counter and label
        self.mistakes = 0
        self.mistakes_label.config(text=f"{self.mistakes}/3")
        # Clear the board (this will reset board state and UI)
        self.clear_board()
        self.status_label.config(text="Left Interactive mode: board cleared and timer reset")

        # Update status for entering modes
        if mode == "mode3":
            self.status_label.config(text="Interactive mode: Fill the board using keyboard!")
        else:
            self.status_label.config(text="Ready")

        # Always unpack both buttons first to reset order
        self.new_game_btn.pack_forget()
        self.prev_game_btn.pack_forget()

        # Handle button visibility based on mode
        if mode == "mode2":
            # Mode 2: Hide "New Game", show "Get Previous Game"
            self.prev_game_btn.pack(before=self.solve_btn, fill='x', pady=5)
        elif mode == "mode3":
            # Mode 3: Show "New Game", hide "Get Previous Game"
            self.new_game_btn.pack(before=self.solve_btn, fill='x', pady=5)
        else:
            # Mode 1: Show both buttons in correct order
            self.new_game_btn.pack(before=self.solve_btn, fill='x', pady=5)
            self.prev_game_btn.pack(before=self.solve_btn, fill='x', pady=5)

    def update_statistics(self):
        """Update puzzle statistics display"""
        empty = sum(1 for i in range(9) for j in range(9) if self.board[i][j] == 0)
        filled = 81 - empty

        self.empty_cells_label.config(text=f"Empty Cells: {empty}")
        self.filled_cells_label.config(text=f"Pre-filled: {filled}")

    def getPreviousGame(self):
        """Retrieve the previous game board"""
        # Check if there's a valid previous board
        has_previous = any(self.previousBoard[i][j] != 0
                          for i in range(9) for j in range(9))

        if has_previous:
            self.board = [row[:] for row in self.previousBoard]
            self.initial_board = [row[:] for row in self.board]
            self.display_board()
            self.update_statistics()
            self.solve_time_label.config(text="Last Solve: -")  # Reset solve time
            self.status_label.config(text="Previous game loaded!")
        else:
            messagebox.showinfo("No Previous Game",
                              "There is no previous game to load!")

    def new_game(self):
        """Generate a new Sudoku puzzle based on mode"""
        mode = self.mode.get()

        if mode == "mode1" or mode == "mode3":
            # Save current board as previous
            if any(self.board[i][j] != 0 for i in range(9) for j in range(9)):
                self.previousBoard = [row[:] for row in self.board]

            # Clear first
            self.clear_board()

            # Generate puzzle based on difficulty
            diff = self.difficulty.get()
            self.board = self.generator.generate_puzzle(diff)
            self.initial_board = [row[:] for row in self.board]
            self.display_board()
            self.update_statistics()
            self.difficulty_label.config(text=f"Difficulty: {diff.capitalize()}")
            self.status_label.config(text=f"New {diff} puzzle generated!")

            if mode == "mode3":
                self.mistakes = 0
                self.mistakes_label.config(text=f"{self.mistakes}/3")
                self.start_timer()

        elif mode == "mode2":
            # Clear board for manual input
            self.clear_board()
            self.status_label.config(text="Enter puzzle and click Solve")

    def display_board(self):
        """Display the current board state"""
        for i in range(9):
            for j in range(9):
                cell = self.cells[(i, j)]
                value = self.board[i][j]

                if value != 0:
                    cell.delete(0, tk.END)
                    cell.insert(0, str(value))
                    # Color pre-filled cells - FIXED: Always use black color
                    if self.initial_board[i][j] != 0:
                        cell.config(state='disabled',
                                  disabledforeground='#000000',  # Black color
                                  disabledbackground='#E8F4F8')
                    else:
                        cell.config(state='normal',
                                  fg='#5470C6',
                                  bg='white')
                else:
                    cell.delete(0, tk.END)
                    cell.config(state='normal', bg='white')

    def get_board_from_gui(self):
        """Read board values from GUI"""
        board = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                val = self.cells[(i, j)].get().strip()
                if val.isdigit() and 1 <= int(val) <= 9:
                    board[i][j] = int(val)
        return board

    def solve_puzzle(self):
        """Solve puzzle using Arc Consistency"""
        self.board = self.get_board_from_gui()
        self.previousBoard = self.get_board_from_gui()

        # Validate input first
        if not self.backtracking_solver.is_valid_board(self.board):
            messagebox.showerror("Invalid Input",
                               "The puzzle configuration is invalid!")
            return

        self.status_label.config(text="Solving with Arc Consistency...")
        self.root.update()

        start_time = time.time()
        solution, arc_tree = self.arc_solver.solve_with_visualization(self.board)
        end_time = time.time()

        if solution:
            self.board = solution
            self.display_board()
            solve_time = end_time - start_time
            self.solve_time_label.config(text=f"Last Solve: {solve_time:.4f}s")
            self.status_label.config(
                text=f"Solved in {solve_time:.4f} seconds using Arc Consistency!")
            self.update_statistics()

            # Store arc tree for visualization
            self.last_arc_tree = arc_tree
        else:
            messagebox.showerror("No Solution",
                               "This puzzle cannot be solved!")

    def solve_puzzle_using_backtrack(self):
        """Solve puzzle using normal backtracking"""
        self.board = self.get_board_from_gui()
        self.previousBoard = self.get_board_from_gui()

        # Validate input first
        if not self.backtracking_solver.is_valid_board(self.board):
            messagebox.showerror("Invalid Input",
                               "The puzzle configuration is invalid!")
            return

        self.status_label.config(text="Solving with normal backtracking...")
        self.root.update()

        start_time = time.time()
        self.backtracking_solver.solve(self.board)
        solution = self.backtracking_solver.solution
        end_time = time.time()

        if solution:
            self.board = solution
            self.display_board()
            solve_time = end_time - start_time
            self.solve_time_label.config(text=f"Last Solve: {solve_time:.4f}s")
            self.status_label.config(
                text=f"Solved in {solve_time:.4f} seconds using Backtracking!")
            self.update_statistics()
        else:
            messagebox.showerror("No Solution",
                               "This puzzle cannot be solved!")

    def clear_board(self):
        """Clear the entire board"""
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.initial_board = [[0 for _ in range(9)] for _ in range(9)]
        for cell in self.cells.values():
            cell.config(state='normal', bg='white')
            cell.delete(0, tk.END)
        self.status_label.config(text="Board cleared")
        self.solve_time_label.config(text="Last Solve: -")
        self.timer_running = False
        self.update_statistics()

    def validate_input(self):
        """Validate if the current board is solvable"""
        self.board = self.get_board_from_gui()

        if self.backtracking_solver.is_valid_board(self.board):
            # Try to solve with backtracking to check solvability
            test_board = [row[:] for row in self.board]
            if self.backtracking_solver.solve(test_board):
                messagebox.showinfo("Valid Input",
                                  "The puzzle is valid and solvable!")
            else:
                messagebox.showwarning("Unsolvable",
                                     "The puzzle is valid but has no solution!")
        else:
            messagebox.showerror("Invalid Input",
                               "The puzzle configuration violates Sudoku rules!")

    def on_cell_focus(self, row, col):
        """Handle cell focus for interactive mode"""
        self.selected_cell = (row, col)

    def on_key_press(self, event, row, col):
        """Handle key press in cells - FIXED: Only allow 1-9"""
        # Check if cell is editable
        if self.initial_board[row][col] != 0:
            return "break"

        # Only allow digits 1-9
        if event.char.isdigit() and '1' <= event.char <= '9':
            num = int(event.char)

            # In interactive mode (mode3), validate the entry
            if self.mode.get() == "mode3":
                self.check_and_insert(row, col, num)
            else:
                # In other modes, just insert without validation
                self.cells[(row, col)].delete(0, tk.END)
                self.cells[(row, col)].insert(0, str(num))
                self.board[row][col] = num

            return "break"
        elif event.keysym == 'BackSpace' or event.keysym == 'Delete':
            self.cells[(row, col)].delete(0, tk.END)
            self.board[row][col] = 0
            return "break"
        else:
            # Block any other input (letters, symbols, 0, etc.)
            return "break"

    def check_and_insert(self, row, col, num):
        """Check if number is valid and insert it (Mode 3 only)"""
        # Check if this violates constraints
        temp_board = [r[:] for r in self.board]
        temp_board[row][col] = num

        if self.backtracking_solver.is_valid_placement(temp_board, row, col, num):
            self.cells[(row, col)].delete(0, tk.END)
            self.cells[(row, col)].insert(0, str(num))
            self.cells[(row, col)].config(fg='#27AE60', bg='#E8F8F0')
            self.board[row][col] = num

            # Reset color after a moment
            self.root.after(300, lambda: self.cells[(row, col)].config(fg='#5470C6', bg='white'))

            # Check if puzzle is complete
            if self.is_complete():
                self.timer_running = False
                messagebox.showinfo("Congratulations!",
                                  "You solved the puzzle correctly!")
        else:
            self.mistakes += 1
            self.mistakes_label.config(text=f"{self.mistakes}/3")
            self.cells[(row, col)].delete(0, tk.END)
            self.cells[(row, col)].insert(0, str(num))
            self.cells[(row, col)].config(fg='#E74C3C', bg='#FADBD8')
            self.root.after(500, lambda: self.cells[(row, col)].delete(0, tk.END))
            self.root.after(500, lambda: self.cells[(row, col)].config(fg='#2C3E50', bg='white'))

            if self.mistakes >= 3:
                self.timer_running = False
                messagebox.showerror("Game Over", "Too many mistakes!")

    def is_complete(self):
        """Check if puzzle is completely filled correctly"""
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return False
        return True

    def start_timer(self):
        """Start the game timer"""
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        """Update timer display"""
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)

    def show_arc_tree(self):
        """Show Arc Consistency tree visualization"""
        if not hasattr(self, 'last_arc_tree') or not self.last_arc_tree:
            messagebox.showinfo("No Tree",
                              "Solve a puzzle first to see the Arc Consistency tree!")
            return

        # Create new window for tree
        tree_window = tk.Toplevel(self.root)
        tree_window.title("Arc Consistency Visualization")
        tree_window.geometry("800x600")

        # Add scrollable text widget
        frame = tk.Frame(tree_window)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        text = tk.Text(frame, wrap='word', font=('Courier', 10))
        scrollbar = tk.Scrollbar(frame, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        text.pack(side='left', fill='both', expand=True)
        
        # Display arc consistency steps
        text.insert('1.0', self.last_arc_tree)
        text.config(state='disabled')

def main():
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()