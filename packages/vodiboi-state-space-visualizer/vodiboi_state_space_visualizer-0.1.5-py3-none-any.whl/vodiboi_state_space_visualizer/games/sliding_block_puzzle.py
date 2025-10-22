from collections import defaultdict
from functools import lru_cache
from itertools import permutations
import math

import numpy as np
import flet as ft

from .game import Game


class SlidingBlockPuzzle(Game):
    """
    Sliding block puzzle (N-puzzle) implementation for state space visualization.
    
    This game represents sliding puzzles like the 8-puzzle or 15-puzzle where
    numbered tiles slide in a grid to reach a goal configuration. The state space
    shows all possible tile arrangements and legal sliding moves between them.

    Example usage:
    ```
    def main(page: ft.Page):
        game = SlidingBlockPuzzle(shape=(3, 3))  # 8-puzzle
        visualizer = FletStateSpaceVisualizer()
        visualizer.build_ui(page, game)
    ft.app(target=main)
    ```
        
    """
    def __init__(self, shape=(3, 3)):
        """
        Args:
            shape (tuple): Grid dimensions as (rows, columns). Default is (3, 3) for 8-puzzle.
        """
        super().__init__()
        self.SHAPE = shape
        self.n, self.m = shape
        self.size = self.n * self.m
        self.button_names = ['Up', 'Down', 'Left', 'Right']
        self.button_dirs = [0, 1, 2, 3]  # up, down, left, right
        self.colorbar_title = "Manhattan Distance"
        self.ignore_leaves = False

    def get_goal_state(self):
        """Get the solved state: [1, 2, 3, ..., n*m-1, 0] where 0 is the empty cell."""
        return tuple(list(range(1, self.size)) + [0])

    def state_to_board(self, state):
        """Convert 1D state tuple to 2D board array."""
        return np.array(state).reshape(self.SHAPE)

    def board_to_state(self, board):
        """Convert 2D board array to 1D state tuple."""
        return tuple(board.flatten())

    def find_empty(self, state):
        """Find the position (row, col) of the empty cell (0)."""
        board = self.state_to_board(state)
        empty_pos = np.where(board == 0)
        return int(empty_pos[0][0]), int(empty_pos[1][0])

    def move(self, state, direction):
        """Move the empty cell in the given direction.
        
        Directions: 0=up, 1=down, 2=left, 3=right
        This moves the empty cell, which is equivalent to moving a numbered tile
        into the empty space from the opposite direction.
        """
        empty_row, empty_col = self.find_empty(state)
        board = self.state_to_board(state).copy()
        
        # Calculate new empty position based on direction
        if direction == 0:  # up - move empty cell up (tile from below moves up)
            new_row, new_col = empty_row - 1, empty_col
        elif direction == 1:  # down - move empty cell down (tile from above moves down)
            new_row, new_col = empty_row + 1, empty_col
        elif direction == 2:  # left - move empty cell left (tile from right moves left)
            new_row, new_col = empty_row, empty_col - 1
        elif direction == 3:  # right - move empty cell right (tile from left moves right)
            new_row, new_col = empty_row, empty_col + 1
        else:
            return state, False

        # Check bounds
        if new_row < 0 or new_row >= self.n or new_col < 0 or new_col >= self.m:
            return state, False

        # Swap empty cell with the tile at new position
        board[empty_row, empty_col], board[new_row, new_col] = board[new_row, new_col], board[empty_row, empty_col]
        
        new_state = self.board_to_state(board)
        return new_state, True

    def spawn_children(self, state):
        """Sliding puzzle is deterministic - no randomness."""
        return [(state, 1.0)]

    def manhattan_distance(self, state):
        """Calculate Manhattan distance heuristic to goal state."""
        board = self.state_to_board(state)
        distance = 0
        
        for i in range(self.n):
            for j in range(self.m):
                value = board[i, j]
                if value != 0:  # Skip empty cell
                    # Calculate where this value should be
                    target_row = (value - 1) // self.m
                    target_col = (value - 1) % self.m
                    # Add Manhattan distance
                    distance += abs(i - target_row) + abs(j - target_col)
        
        return distance

    def board_score(self, state):
        """Score based on negative Manhattan distance (higher = better)."""
        return -self.manhattan_distance(state)

    def canonical(self, state):
        """For sliding puzzle, return state as-is since rotations change the puzzle."""
        return state

    @lru_cache(None)
    def expected_score(self, state):
        """Simple heuristic: negative Manhattan distance."""
        return self.board_score(state)

    def is_solvable(self, state):
        """Check if the puzzle state is solvable using inversion count."""
        # Convert to list without empty cell for inversion counting
        tiles = [x for x in state if x != 0]
        
        # Count inversions
        inversions = 0
        for i in range(len(tiles)):
            for j in range(i + 1, len(tiles)):
                if tiles[i] > tiles[j]:
                    inversions += 1
        
        # For odd width: solvable if inversions are even
        if self.m % 2 == 1:
            return inversions % 2 == 0
        
        # For even width: depends on empty cell row from bottom
        empty_row, _ = self.find_empty(state)
        empty_row_from_bottom = self.n - empty_row
        
        if empty_row_from_bottom % 2 == 1:  # Empty on odd row from bottom
            return inversions % 2 == 0
        else:  # Empty on even row from bottom
            return inversions % 2 == 1

    def enumerate_states(self, initial_tiles=None, ALL_STATES=False, ignore_leaves=False):
        """Enumerate states for sliding puzzle.
        
        If ALL_STATES=True, generates all (n*m)! possible board configurations.
        If ALL_STATES=False, only generates reachable states from goal state.
        """
        goal_state = self.get_goal_state()
        edges = defaultdict(float)
        
        if ALL_STATES:
            # Generate all possible permutations of tiles (0 through n*m-1)
            
            
            print(f"Generating all {self.size}! = {math.factorial(self.size)} possible board states...")
            
            # Create all permutations of numbers 0 to (n*m-1)
            all_tiles = list(range(self.size))
            all_permutations = list(permutations(all_tiles))
            
            # Convert to valid sliding puzzle states (use 1-(n*m-1) and 0 for empty)
            all_states = set()
            for perm in all_permutations:
                # Convert: 0->0 (empty), 1->1, 2->2, etc.
                state = tuple(perm)
                all_states.add(state)
            
            visited = all_states
            
            # Generate edges between all states (if they can reach each other in one move)
            print(f"Computing edges for {len(visited)} states...")
            for state in visited:
                for direction in self.button_dirs:
                    new_state, changed = self.move(state, direction)
                    if changed and new_state in visited:
                        state_can = self.canonical(state)
                        new_state_can = self.canonical(new_state)
                        if state_can != new_state_can:
                            edges[(state_can, new_state_can)] = 1
        else:
            # Original logic: only reachable states from goal
            visited = {goal_state}
            queue = [goal_state]
            
            # Limit exploration for larger puzzles to avoid exponential explosion
            # max_states = 1000 if self.size <= 9 else 500 if self.size <= 12 else 200
            
            while queue:
                print(len(visited), end='\r')
                state = queue.pop(0)
                
                # Try all possible moves
                for direction in self.button_dirs:
                    new_state, changed = self.move(state, direction)
                    if changed:
                        state_can = self.canonical(state)
                        new_state_can = self.canonical(new_state)
                        
                        if state_can != new_state_can:
                            edges[(state_can, new_state_can)] = 1
                        
                        if new_state_can not in visited:
                            visited.add(new_state_can)
                            queue.append(new_state_can)

        nodes = list(visited)
        idx = {s: i for i, s in enumerate(nodes)}
        edges_w = [(idx[u], idx[v], w) for (u, v), w in edges.items()]

        labels = {}
        for i, s in enumerate(nodes):
            labels[i] = {
                'state': s,
                'max_tile': max(s),  # Highest numbered tile
                'nnz': len([x for x in s if x != 0]),  # Non-zero tiles
                'sum_exp': sum(s),  # Sum of all tiles
                'expected_score': self.expected_score(s),
            }
        
        return nodes, edges_w, labels

    def state_scalar(self, state):
        """Return negative Manhattan distance for coloring (0 = goal, higher = farther)."""
        return self.manhattan_distance(state)

    def board_to_display(self, state):
        """Return string representation of the board."""
        board = self.state_to_board(state)
        display_board = board.copy()
        display_board[display_board == 0] = -1  # Replace 0 with -1 for display
        return str(display_board.tolist()).replace('-1', '·')

    def board_annotations(self, board):
        """Return annotations for displaying the puzzle."""
        anns = []
        n, m = board.shape
        
        for i in range(n):
            for j in range(m):
                val = int(board[i, j])
                text = str(val) if val != 0 else '·'
                color = 'blue' if val != 0 else 'lightgray'
                anns.append(dict(
                    x=j, y=n-1-i, text=text, 
                    xanchor='center', yanchor='middle', 
                    showarrow=False, 
                    font=dict(color=color, size=24)
                ))
        return anns

    def initial_state(self, nodes, edges_w, labels):
        """For Sliding Puzzle, restart to goal state (solved state)."""
        goal_state = self.get_goal_state()
        goal_state_canonical = self.canonical(goal_state)
        state_to_idx = {labels[j]['state']: j for j in range(len(labels))}
        return state_to_idx.get(goal_state_canonical, 0)

    def get_restart_desc(self):
        """Return restart button description for Sliding Puzzle."""
        return "Restart (Solved State)"

    def flet_display(self, state):
        """Create a Flet display for the Sliding Puzzle game board."""
        
        board = self.state_to_board(state)
        n, m = self.SHAPE
        
        # Create grid container
        board_container = ft.Column(spacing=2, alignment=ft.MainAxisAlignment.CENTER)
        
        for i in range(n):
            row_controls = []
            for j in range(m):
                cell_value = int(board[i, j])
                
                if cell_value == 0:
                    # Empty cell
                    cell_container = ft.Container(
                        content=ft.Text("", text_align=ft.TextAlign.CENTER),
                        width=50,
                        height=50,
                        bgcolor=ft.Colors.GREY_300,
                        border_radius=5,
                        alignment=ft.alignment.center,
                        border=ft.border.all(2, ft.Colors.GREY_500)
                    )
                else:
                    # Numbered cell
                    cell_container = ft.Container(
                        content=ft.Text(
                            str(cell_value),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER
                        ),
                        width=50,
                        height=50,
                        bgcolor=ft.Colors.BLUE_400,
                        border_radius=5,
                        alignment=ft.alignment.center,
                        border=ft.border.all(2, ft.Colors.BLUE_600)
                    )
                
                row_controls.append(cell_container)
            
            board_container.controls.append(
                ft.Row(row_controls, spacing=2, alignment=ft.MainAxisAlignment.CENTER)
            )
        
        return ft.Container(
            content=board_container,
            padding=20,
            bgcolor=ft.Colors.GREY_700,
            border_radius=10,
            alignment=ft.alignment.center
        )
