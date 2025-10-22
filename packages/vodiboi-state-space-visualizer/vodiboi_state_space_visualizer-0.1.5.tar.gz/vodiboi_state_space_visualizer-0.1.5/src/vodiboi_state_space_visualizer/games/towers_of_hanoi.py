from collections import defaultdict
from functools import lru_cache
import itertools

import numpy as np
import flet as ft

from .game import Game


class TowersOfHanoi(Game):
    """
    Towers of Hanoi puzzle implementation for state space visualization.
    
    This game represents the classic Towers of Hanoi puzzle where players
    move disks between towers following the rule that larger disks cannot
    be placed on top of smaller ones. The state space shows all valid
    configurations and legal moves between them.

    Example usage:
    ```
    def main(page: ft.Page):
        game = TowersOfHanoi(num_disks=3, num_towers=3)
        visualizer = FletStateSpaceVisualizer()
        visualizer.build_ui(page, game)
    ft.app(target=main)
    ```
        
    """
    def __init__(self, num_disks=3, num_towers=3):
        """
        Args:
            num_disks (int): Number of disks in the puzzle. Default is 3.
            num_towers (int): Number of towers/pegs. Default is 3.
        """
        super().__init__()
        self.num_disks = num_disks
        self.num_towers = num_towers
        self.SHAPE = (num_disks, num_towers)  # Display as num_disks rows x num_towers towers
        
        # Generate button names and directions for all tower pairs
        self.button_names = []
        self.button_dirs = []
        for from_tower in range(num_towers):
            for to_tower in range(num_towers):
                if from_tower != to_tower:
                    self.button_names.append(f'{from_tower}→{to_tower}')
                    self.button_dirs.append((from_tower, to_tower))
        
        self.colorbar_title = "Disks on target tower"
        self.ignore_leaves = False

    def state_to_towers(self, state):
        """Convert state tuple to list of towers (lists of disks).
        In each tower list, index 0 = bottom (largest disk), last index = top (smallest disk).
        """
        towers = [[] for _ in range(self.num_towers)]
        for i, tower_id in enumerate(state):
            disk_size = i + 1  # disk sizes are 1-based
            towers[tower_id].append(disk_size)
        # Sort each tower so largest disks are at bottom (start of list), smallest at top (end)
        for tower in towers:
            tower.sort(reverse=True)
        return towers

    def towers_to_state(self, towers):
        """Convert list of towers back to state tuple."""
        state = [0] * self.num_disks
        for tower_id, tower in enumerate(towers):
            for disk_size in tower:
                state[disk_size - 1] = tower_id  # disk_size is 1-based, index is 0-based
        return tuple(state)

    def is_valid_move(self, towers, from_tower, to_tower):
        """Check if moving top disk from from_tower to to_tower is valid."""
        if not towers[from_tower]:  # from_tower is empty
            return False
        if not towers[to_tower]:  # to_tower is empty
            return True
        # Can only place smaller disk on larger disk
        # Top disk is at end of list (smallest number = smaller disk)
        return towers[from_tower][-1] < towers[to_tower][-1]

    def move(self, state, direction):
        """Move top disk from one tower to another."""
        from_tower, to_tower = direction
        towers = self.state_to_towers(state)
        
        if not self.is_valid_move(towers, from_tower, to_tower):
            return state, False
        
        # Perform the move
        disk = towers[from_tower].pop()
        towers[to_tower].append(disk)
        
        new_state = self.towers_to_state(towers)
        return new_state, True

    def spawn_children(self, state):
        """In Hanoi, there's no randomness - just return the state with probability 1."""
        return [(state, 1.0)]

    def board_score(self, state):
        """Score based on how many disks are on the target tower (last tower)."""
        towers = self.state_to_towers(state)
        target_tower = self.num_towers - 1
        return len(towers[target_tower])

    def canonical(self, state):
        """For Towers of Hanoi, return the state as-is.
        
        We don't apply symmetry transformations because:
        1. The last tower is the designated target tower (not symmetric with others)
        2. Each state represents a specific configuration that should be preserved
        3. Players expect to see their exact moves reflected in the visualization
        """
        return state

    @lru_cache(None)
    def expected_score(self, state):
        """For Hanoi, this is the minimum number of moves to solve."""
        towers = self.state_to_towers(state)
        target_tower_idx = self.num_towers - 1
        target_tower = towers[target_tower_idx]
        
        # If all disks are on target tower in correct order, score is high
        if len(target_tower) == self.num_disks and target_tower == list(range(self.num_disks, 0, -1)):
            return 1000  # High score for solved state
        
        # Otherwise, score based on progress (disks on target tower)
        return len(target_tower) * 10

    def enumerate_states(self, initial_tiles=None, ALL_STATES=True, ignore_leaves=False):
        """Enumerate states in Towers of Hanoi.
        
        If ALL_STATES=True: Generate all valid Hanoi configurations (respecting disk ordering rules)
        If ALL_STATES=False: Only generate states reachable from initial position
        """
        if ALL_STATES:
            # Generate ALL valid Hanoi configurations
            # Generate all possible assignments of disks to towers
            valid_states = []
            
            # Each disk can be on any tower: num_towers choices for each of num_disks disks
            for state_tuple in itertools.product(range(self.num_towers), repeat=self.num_disks):
                state = tuple(state_tuple)
                
                # Check if this state is valid (respects Hanoi rules)
                if self.is_valid_hanoi_state(state):
                    valid_states.append(state)
            
            # Build edges between all valid states
            edges = defaultdict(float)
            for state in valid_states:
                for direction in self.button_dirs:
                    new_state, changed = self.move(state, direction)
                    if changed and new_state in valid_states:
                        state_can = self.canonical(state)
                        new_state_can = self.canonical(new_state)
                        if state_can != new_state_can:
                            edges[(state_can, new_state_can)] = 1
            
            nodes = valid_states
        else:
            # Original behavior: only reachable states from initial position
            initial_state = tuple([0] * self.num_disks)
            
            visited = {initial_state}
            queue = [initial_state]
            edges = defaultdict(float)
            
            while queue:
                state = queue.pop(0)
                
                # Try all possible moves
                for direction in self.button_dirs:
                    new_state, changed = self.move(state, direction)
                    if changed:
                        new_state_can = self.canonical(new_state)
                        state_can = self.canonical(state)
                        
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
            towers = self.state_to_towers(s)
            target_tower_idx = self.num_towers - 1
            labels[i] = {
                'state': s,
                'max_tile': len(towers[target_tower_idx]),  # disks on target tower
                'nnz': self.num_disks,  # always same number of disks
                'sum_exp': sum(len(tower) for tower in towers),  # always num_disks
                'expected_score': self.expected_score(s),
            }
        
        return nodes, edges_w, labels

    def is_valid_hanoi_state(self, state):
        """Check if a state respects Hanoi rules (smaller disks on top of larger disks)."""
        towers = self.state_to_towers(state)
        
        # Check each tower: disks should be in decreasing order (largest at bottom)
        for tower in towers:
            # tower is already sorted by state_to_towers: [largest...smallest] (bottom to top)
            # Check that each disk is smaller than the one below it
            for i in range(len(tower) - 1):
                if tower[i] <= tower[i + 1]:  # Bottom disk should be larger than top disk
                    return False
        
        return True

    def state_scalar(self, state):
        """Return number of disks on target tower for coloring."""
        towers = self.state_to_towers(state)
        target_tower = self.num_towers - 1
        return len(towers[target_tower])

    def state_to_2d_array(self, state):
        """Convert Hanoi state to 2D array for visualization.
        Bottom row = bottom of tower, top row = top of tower.
        """
        towers = self.state_to_towers(state)
        array = np.zeros(self.SHAPE)
        
        # Fill array with disk positions
        # towers[i] has disks sorted: [largest...smallest] (bottom to top)
        for tower_id, tower in enumerate(towers):
            for pos, disk_size in enumerate(tower):
                if pos < self.num_disks:  # Safety check
                    # Put disk at correct position: pos=0 (largest) goes to bottom row
                    array[self.num_disks - 1 - pos, tower_id] = disk_size
        
        return array

    def board_to_display(self, state):
        """Return string representation of the towers."""
        towers = self.state_to_towers(state)
        tower_strs = [f"T{i}:{tower}" for i, tower in enumerate(towers)]
        return " ".join(tower_strs)

    def board_annotations(self, board):
        """Return annotations for displaying the towers."""
        # For Hanoi, we'll create a display with one column per tower
        anns = []
        
        # Treat board as (num_disks)x(num_towers) grid showing towers
        if hasattr(board, 'shape') and len(board.shape) == 2:
            n, m = board.shape
            for i in range(n):
                for j in range(m):
                    val = int(board[i, j]) if board[i, j] > 0 else 0
                    text = str(val) if val > 0 else '·'
                    anns.append(dict(
                        x=j, y=n-1-i, text=text, 
                        xanchor='center', yanchor='middle', 
                        showarrow=False, 
                        font=dict(color='blue', size=24)
                    ))
        return anns

    def initial_state(self, nodes, edges_w, labels):
        """For Towers of Hanoi, initial state is all disks on tower 0."""
        initial_state = tuple([0] * self.num_disks)
        initial_state_canonical = self.canonical(initial_state)
        state_to_idx = {labels[j]['state']: j for j in range(len(labels))}
        return state_to_idx.get(initial_state_canonical, 0)

    def get_restart_desc(self):
        """Return restart button description for Towers of Hanoi."""
        return "Restart (All on Tower 0)"

    def flet_display(self, state):
        """Create a Flet display for the Towers of Hanoi game board."""

        towers = self.state_to_towers(state)

        # Dynamically scale tower width and height based on number of towers/disks
        num_towers = self.num_towers
        num_disks = self.num_disks

        # Make towers and disks smaller as number increases
        max_total_width = 400
        max_total_height = 220
        min_tower_width = 40
        min_tower_height = 100
        max_tower_width = 120
        max_tower_height = 200

        tower_width = max(min_tower_width, min(max_tower_width, int(max_total_width / (num_towers + 0.5))))
        tower_height = max(min_tower_height, min(max_tower_height, int(max_total_height - 8 * (num_towers - 3) - 5 * (num_disks - 3))))

        disk_height = max(12, min(22, int(tower_height / (num_disks + 2))))
        disk_min_width = int(tower_width * 0.25)
        disk_max_width = int(tower_width * 0.95)

        tower_containers = []

        for tower_idx, tower in enumerate(towers):
            # Create disk containers (largest at bottom)
            disk_containers = []
            for disk_size in tower:
                # Larger disk numbers = larger visual size
                disk_width = disk_min_width + disk_size * int((disk_max_width - disk_min_width) / max(num_disks, 1))
                disk_width = min(disk_width, disk_max_width)
                colors = [
                    ft.Colors.RED_400, ft.Colors.BLUE_400, ft.Colors.GREEN_400,
                    ft.Colors.YELLOW_400, ft.Colors.PURPLE_400, ft.Colors.ORANGE_400,
                    ft.Colors.PINK_400, ft.Colors.CYAN_400
                ]
                disk_color = colors[(disk_size - 1) % len(colors)]

                disk = ft.Container(
                    content=ft.Text(
                        str(disk_size),
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        size=12
                    ),
                    width=disk_width,
                    height=disk_height,
                    bgcolor=disk_color,
                    border_radius=5,
                    alignment=ft.alignment.center,
                    border=ft.border.all(2, ft.Colors.BLACK)
                )
                disk_containers.append(disk)

            # Add tower base and pole
            tower_base = ft.Container(
                width=int(tower_width * 0.85),
                height=8,
                bgcolor=ft.Colors.BROWN_400,
                border_radius=2
            )
            tower_pole = ft.Container(
                width=6,
                height=int(tower_height * 0.75),
                bgcolor=ft.Colors.BROWN_600,
                border_radius=3
            )

            # Stack elements: disks (largest first), then pole, then base
            tower_stack = ft.Stack(
                controls=[
                    ft.Container(
                        content=tower_pole,
                        alignment=ft.alignment.bottom_center,
                        margin=ft.margin.only(bottom=8)
                    ),
                    ft.Container(
                        content=tower_base,
                        alignment=ft.alignment.bottom_center
                    )
                ] + [
                    ft.Container(
                        content=disk,
                        alignment=ft.alignment.bottom_center,
                        margin=ft.margin.only(bottom=8 + idx * (disk_height + 2))
                    ) for idx, disk in enumerate(disk_containers)
                ],
                height=tower_height,
                width=tower_width
            )

            # Tower with label
            tower_with_label = ft.Column([
                tower_stack,
                ft.Text(
                    f"Tower {tower_idx}",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    color=ft.Colors.WHITE
                )
            ], alignment=ft.MainAxisAlignment.CENTER,
               horizontal_alignment=ft.CrossAxisAlignment.CENTER)

            tower_containers.append(tower_with_label)

        return ft.Container(
            content=ft.Row(
                tower_containers,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=max(6, int(24 * (3 / num_towers)))
            ),
            padding=16,
            bgcolor=ft.Colors.GREY_800,
            border_radius=10,
            alignment=ft.alignment.center
        )

