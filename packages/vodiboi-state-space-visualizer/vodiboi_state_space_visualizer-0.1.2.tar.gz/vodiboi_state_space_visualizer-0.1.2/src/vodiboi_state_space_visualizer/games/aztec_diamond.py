from collections import defaultdict
from dataclasses import dataclass
from typing import FrozenSet, Set, List, Tuple
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import flet as ft

from .game import Game

Cell = Tuple[int, int]
Domino = FrozenSet[Cell]
Tiling = FrozenSet[Domino]
Plaquette = Tuple[int, int]


class AztecDiamond(Game):
    """
    Aztec Diamond Tilings game implementation.
    
    This game represents domino tilings of an Aztec diamond region, where players
    can flip between valid tilings using plaquette operations.

    Example usage:
    ```
    def main(page: ft.Page):
        game = AztecDiamond(n=3)
        visualizer = FletStateSpaceVisualizer(ALL_STATES=True)
        visualizer.build_ui(page, game)
    ft.app(target=main)
    ```
        
    """
    def __init__(self, n=3):
        """
        Args:
            n (int): Order of the Aztec diamond
        """
        super().__init__()
        self.n = n
        self.SHAPE = (2*n, 2*n)  # Approximate shape for visualization
        
        # Initialize the Aztec diamond region
        self.cells = self.make_cells(n)
        self.plaquettes = self.list_plaquettes(self.cells)
        
        # Generate all valid tilings
        self.tilings = self.enumerate_tilings(self.cells)
        
        # Set up button configuration
        self.button_names = ["🔄 Flip Random"]
        self.button_dirs = [0]
        self.colorbar_title = "Vertical Dominoes Count"
        self.ignore_leaves = False
        
        # State for interactive tile selection
        self.selected_tiles = []  # Track selected tiles for flipping
        self.max_selected = 2     # Allow selecting 2 tiles
        
        # Color mapping for domino directions (Wikipedia style)
        self.COLORS = {
            'E': '#FFEB3B',  # yellow (East)
            'N': '#00C853',  # green (North)
            'W': '#2962FF',  # blue (West)
            'S': '#F44336',  # red (South)
        }
    
    def make_cells(self, n: int) -> Set[Cell]:
        """Create the order n Aztec diamond with 2*n*(n+1) cells."""
        cells = set()
        for r in range(2*n):
            j = r - (n - 1)
            m = min(r, 2*n - 1 - r)
            L = 2 * (m + 1)
            k = L // 2
            for i in range(-k, k):
                cells.add((i, j))
        return cells
    
    def neighbors4(self, c: Cell) -> List[Cell]:
        """Get the 4-connected neighbors of a cell."""
        i, j = c
        return [(i+1, j), (i-1, j), (i, j+1), (i, j-1)]
    
    def is_adjacent(self, c1: Cell, c2: Cell) -> bool:
        """Check if two cells are adjacent."""
        return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) == 1
    
    def enumerate_tilings(self, cells: Set[Cell]) -> List[Tiling]:
        """Enumerate all valid domino tilings using backtracking."""
        cells = set(cells)
        N = len(cells)
        assert N % 2 == 0, "Region must have even number of cells."
        
        # Build adjacency list
        adj = {c: [n for n in self.neighbors4(c) if n in cells] for c in cells}
        
        tilings = []
        
        def backtrack(uncovered: Set[Cell], acc: List[Domino]):
            if not uncovered:
                tilings.append(frozenset(acc))
                return
            
            c = min(uncovered)
            for nb in adj[c]:
                if nb not in uncovered:
                    continue
                
                d = frozenset((c, nb))
                uncovered.remove(c)
                uncovered.remove(nb)
                acc.append(d)
                backtrack(uncovered, acc)
                acc.pop()
                uncovered.add(nb)
                uncovered.add(c)
        
        backtrack(set(cells), [])
        return tilings
    
    def list_plaquettes(self, cells: Set[Cell]) -> List[Plaquette]:
        """List all 2x2 plaquettes (unit squares) fully contained in the region."""
        S = set(cells)
        xs = [i for i, _ in S]
        ys = [j for _, j in S]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        
        res = []
        for x in range(xmin-1, xmax+1):
            for y in range(ymin-1, ymax+1):
                block = {(x, y), (x+1, y), (x, y+1), (x+1, y+1)}
                if block.issubset(S):
                    res.append((x, y))
        return res
    
    def cells_of_plaquette(self, p: Plaquette) -> Tuple[Cell, Cell, Cell, Cell]:
        """Get the four cells of a plaquette."""
        x, y = p
        return ((x, y), (x+1, y), (x, y+1), (x+1, y+1))
    
    def find_flippable(self, T: Tiling) -> List[Plaquette]:
        """Find all plaquettes that can be flipped in the current tiling."""
        c2d = {}
        for d in T:
            a, b = tuple(d)
            c2d[a] = d
            c2d[b] = d
        
        flippable = []
        for p in self.plaquettes:
            a, b, c, d = self.cells_of_plaquette(p)
            try:
                D1, D2, D3, D4 = c2d[a], c2d[b], c2d[c], c2d[d]
            except KeyError:
                continue
            
            doms = {D1, D2, D3, D4}
            if len(doms) != 2:
                continue
            
            # Check if it's either horizontal pair or vertical pair
            horiz = (frozenset((a, b)) in doms and frozenset((c, d)) in doms)
            vert = (frozenset((a, c)) in doms and frozenset((b, d)) in doms)
            if horiz or vert:
                flippable.append(p)
        
        return flippable
    
    def flip(self, T: Tiling, p: Plaquette) -> Tiling:
        """Flip a plaquette in the tiling."""
        a, b, c, d = self.cells_of_plaquette(p)
        
        # Map cells to dominoes
        c2d = {}
        for dmn in T:
            for cc in dmn:
                c2d[cc] = dmn
        
        doms = list({c2d[a], c2d[b], c2d[c], c2d[d]})
        horiz = (frozenset((a, b)) in doms and frozenset((c, d)) in doms)
        vert = (frozenset((a, c)) in doms and frozenset((b, d)) in doms)
        
        if not (horiz or vert):
            raise ValueError("Plaquette not flippable")
        
        if horiz:
            new1 = frozenset((a, c))
            new2 = frozenset((b, d))
        else:
            new1 = frozenset((a, b))
            new2 = frozenset((c, d))
        
        Tset = set(T)
        for dmn in doms:
            Tset.remove(dmn)
        Tset.add(new1)
        Tset.add(new2)
        
        return frozenset(Tset)
    
    def tiling_to_state(self, tiling: Tiling) -> tuple:
        """Convert a tiling to a state tuple for compatibility."""
        # Use a sorted representation of the tiling for consistency
        domino_list = []
        for domino in tiling:
            cells = tuple(sorted(tuple(domino)))
            domino_list.append(cells)
        return tuple(sorted(domino_list))
    
    def state_to_tiling(self, state: tuple) -> Tiling:
        """Convert a state tuple back to a tiling."""
        dominoes = []
        for domino_cells in state:
            dominoes.append(frozenset(domino_cells))
        return frozenset(dominoes)
    
    def count_vertical_dominoes(self, tiling: Tiling) -> int:
        """Count the number of vertical dominoes in a tiling."""
        count = 0
        for domino in tiling:
            (i1, j1), (i2, j2) = tuple(domino)
            if i1 == i2:  # Same x-coordinate means vertical
                count += 1
        return count
    
    def move(self, state, direction):
        """Perform a move (flip operation) on the current state."""
        
        tiling = self.state_to_tiling(state)
        flippable = self.find_flippable(tiling)
        
        if not flippable:
            return state, False
        
        # Only random flip is available now
        p = random.choice(flippable)
        
        new_tiling = self.flip(tiling, p)
        new_state = self.tiling_to_state(new_tiling)
        return new_state, True

    def on_tile_click(self, position):
        """Handle clicking on a tile for selection."""
        row, col = position
        
        if position in self.selected_tiles:
            # Deselect if already selected
            self.selected_tiles.remove(position)
        else:
            # Select if not already selected
            if len(self.selected_tiles) < self.max_selected:
                self.selected_tiles.append(position)
            else:
                # Replace oldest selection if at max
                self.selected_tiles.pop(0)
                self.selected_tiles.append(position)
        
        print(f"Selected tiles: {self.selected_tiles}")

    def clear_tile_selection(self, e=None):
        """Clear all selected tiles."""
        self.selected_tiles = []
        print("Selection cleared")

    def get_plaquette_cells(self, plaquette_pos):
        """Get all 4 cells in a 2x2 plaquette."""
        row, col = plaquette_pos
        return [
            (row, col), (row, col + 1),
            (row + 1, col), (row + 1, col + 1)
        ]

    def flip_selected_tiles(self, current_state):
        """Attempt to flip the two selected tiles."""
        if len(self.selected_tiles) != 2:
            print(f"Need exactly 2 tiles selected, have {len(self.selected_tiles)}")
            return current_state, False
        
        pos1, pos2 = self.selected_tiles
        tiling = self.state_to_tiling(current_state)
        
        # Create a mapping from cell positions to dominoes
        cell_to_domino = {}
        for domino in tiling:
            (i1, j1), (i2, j2) = tuple(domino)
            cell_to_domino[(i1, j1)] = domino
            cell_to_domino[(i2, j2)] = domino
        
        # Check if both positions are in cells within the diamond
        if pos1 not in cell_to_domino or pos2 not in cell_to_domino:
            print(f"Invalid selection: one or both tiles are not in the diamond")
            return current_state, False
        
        # Get the dominoes at these positions
        domino1 = cell_to_domino[pos1]
        domino2 = cell_to_domino[pos2]
        
        # Must be the same domino 
        if domino1 != domino2:
            print(f"Invalid selection: tiles must be parts of the same domino")
            print(f"  Tile {pos1}: domino {domino1}")  
            print(f"  Tile {pos2}: domino {domino2}")
            return current_state, False
        
        # Check if they're adjacent (form a valid domino)
        row1, col1 = pos1
        row2, col2 = pos2
        
        is_adjacent = (abs(row1 - row2) == 1 and col1 == col2) or \
                      (row1 == row2 and abs(col1 - col2) == 1)
        
        if not is_adjacent:
            print(f"Invalid selection: tiles must be adjacent")
            return current_state, False
        
        # Check if this domino can be flipped (part of a flippable 2x2 plaquette)
        flippable_plaquettes = self.find_flippable(tiling)
        
        # Find which plaquette contains this domino
        target_plaquette = None
        for plaquette_pos in flippable_plaquettes:
            plaquette_cells = self.get_plaquette_cells(plaquette_pos)
            if pos1 in plaquette_cells and pos2 in plaquette_cells:
                target_plaquette = plaquette_pos
                break
        
        if target_plaquette is None:
            print(f"Selected domino cannot be flipped (not part of a flippable 2x2 plaquette)")
            return current_state, False
        
        # Perform the flip
        print(f"Flipping domino at {pos1}, {pos2} via plaquette {target_plaquette}")
        new_tiling = self.flip(tiling, target_plaquette)
        new_state = self.tiling_to_state(new_tiling)
        
        # Clear selection
        self.clear_tile_selection()
        return new_state, True

    def spawn_children(self, state):
        """Aztec Diamond is deterministic - no randomness in state transitions."""
        return [(state, 1.0)]
    
    def board_score(self, state):
        """Score based on the number of vertical dominoes."""
        tiling = self.state_to_tiling(state)
        return self.count_vertical_dominoes(tiling)
    
    def canonical(self, state):
        """Return canonical form of state."""
        return state
    
    def expected_score(self, state):
        """Expected score heuristic."""
        return self.board_score(state)
    
    def enumerate_states(self, initial_tiles=None, ALL_STATES=True, ignore_leaves=False):
        """Enumerate states for Aztec Diamond tilings."""
        
        # Convert all tilings to states
        states = [self.tiling_to_state(t) for t in self.tilings]
        
        # Build transition graph
        edges = defaultdict(float)
        
        for i, state in enumerate(states):
            tiling = self.state_to_tiling(state)
            flippable = self.find_flippable(tiling)
            
            for p in flippable:
                new_tiling = self.flip(tiling, p)
                new_state = self.tiling_to_state(new_tiling)
                
                # Find the index of the new state
                try:
                    j = states.index(new_state)
                    edges[(i, j)] = 1.0
                except ValueError:
                    continue
        
        # Convert to edge list
        edges_w = [(u, v, w) for (u, v), w in edges.items()]
        
        # Create labels
        labels = {}
        for i, state in enumerate(states):
            tiling = self.state_to_tiling(state)
            labels[i] = {
                'state': state,
                'expected_score': self.expected_score(state),
                'vertical_count': self.count_vertical_dominoes(tiling),
                'flippable_count': len(self.find_flippable(tiling))
            }
        
        return states, edges_w, labels
    
    def state_scalar(self, state):
        """Return number of vertical dominoes for coloring."""
        tiling = self.state_to_tiling(state)
        return self.count_vertical_dominoes(tiling)
    
    def board_to_display(self, state):
        """Return string representation of the state."""
        tiling = self.state_to_tiling(state)
        return f"Tiling with {len(tiling)} dominoes ({self.count_vertical_dominoes(tiling)} vertical)"
    
    def board_annotations(self, board):
        """Return annotations for displaying the Aztec Diamond tiling."""
        # For Aztec Diamond, we'll show the domino structure
        # This is called when visualizing in Plotly
        anns = []
        
        # If board is actually a state, convert it
        if isinstance(board, tuple):
            tiling = self.state_to_tiling(board)
        else:
            # Assume it's already a tiling or can be converted
            tiling = board if isinstance(board, frozenset) else self.state_to_tiling(board)
        
        # Add annotations for each domino
        for i, domino in enumerate(tiling):
            (x1, y1), (x2, y2) = tuple(domino)
            
            # Center of the domino
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            
            # Get direction and color info
            try:
                direction = self.domino_direction(domino)
                direction_colors = {
                    'E': 'gold', 'N': 'green', 'W': 'blue', 'S': 'red'
                }
                color = direction_colors.get(direction, 'gray')
            except:
                direction = '?'
                color = 'gray'
            
            anns.append(dict(
                x=cx, y=cy, 
                text=direction,
                xanchor='center', yanchor='middle',
                showarrow=False,
                font=dict(color='white', size=10, family='Arial Black'),
                bgcolor=color,
                bordercolor='black',
                borderwidth=1
            ))
        
        return anns
    
    def create_matplotlib_visualization(self, state, figsize=(8, 6), save_path=None):
        """Create a matplotlib visualization of the Aztec Diamond tiling."""
        
        tiling = self.state_to_tiling(state)
        
        # Calculate bounds
        xs = [i for i, _ in self.cells]
        ys = [j for _, j in self.cells]
        xmin, xmax = min(xs) - 0.5, max(xs) + 0.5
        ymin, ymax = min(ys) - 0.5, max(ys) + 0.5
        
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_aspect('equal')
        ax.set_xlim(xmin - 0.5, xmax + 0.5)
        ax.set_ylim(ymin - 0.5, ymax + 0.5)
        ax.set_title(f'Aztec Diamond Tiling (n={self.n})', fontsize=14, fontweight='bold')
        
        # Color mapping matching the notebook
        matplotlib_colors = {
            'E': '#FFEB3B',  # Yellow (East)
            'N': '#00C853',  # Green (North)
            'W': '#2962FF',  # Blue (West)
            'S': '#F44336',  # Red (South)
        }
        
        # Draw each domino
        for domino in tiling:
            (i1, j1), (i2, j2) = tuple(domino)
            
            # Determine rectangle position and size
            if i1 == i2:  # Vertical domino
                x = i1 - 0.5
                y = min(j1, j2) - 0.5
                width, height = 1.0, 2.0
            else:  # Horizontal domino
                x = min(i1, i2) - 0.5
                y = j1 - 0.5
                width, height = 2.0, 1.0
            
            # Get direction and color
            try:
                direction = self.domino_direction(domino)
                color = matplotlib_colors[direction]
            except:
                direction = '?'
                color = '#CCCCCC'
            
            # Create and add rectangle
            rect = Rectangle((x, y), width, height,
                           linewidth=2, edgecolor='black',
                           facecolor=color, alpha=0.8)
            ax.add_patch(rect)
            
            # Add direction label
            cx = x + width / 2
            cy = y + height / 2
            ax.text(cx, cy, direction, ha='center', va='center',
                   fontsize=10, fontweight='bold', color='white',
                   bbox=dict(boxstyle='round,pad=0.1', facecolor='black', alpha=0.7))
        
        # Add grid to show cell structure
        for x in range(int(xmin), int(xmax) + 2):
            ax.axvline(x - 0.5, color='gray', alpha=0.3, linewidth=0.5)
        for y in range(int(ymin), int(ymax) + 2):
            ax.axhline(y - 0.5, color='gray', alpha=0.3, linewidth=0.5)
        
        # Add legend
        legend_elements = [
            plt.Rectangle((0,0),1,1, facecolor=color, edgecolor='black', label=f'{direction}')
            for direction, color in matplotlib_colors.items()
        ]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.05, 1))
        
        # Style
        ax.set_xlabel('X coordinate', fontsize=12)
        ax.set_ylabel('Y coordinate', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Add statistics text
        vertical_count = self.count_vertical_dominoes(tiling)
        horizontal_count = len(tiling) - vertical_count
        flippable_count = len(self.find_flippable(tiling))
        
        stats_text = f'Total: {len(tiling)} dominoes\nVertical: {vertical_count}, Horizontal: {horizontal_count}\nFlippable: {flippable_count} plaquettes'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved visualization to {save_path}")
        
        return fig, ax
    
    def initial_state(self, nodes, edges_w, labels):
        """Return the index of an initial state (first tiling)."""
        return 0
    
    def get_restart_desc(self):
        """Return restart button description."""
        return "Restart (First Tiling)"
    
    def cell_parity(self, i: int, j: int) -> str:
        """Determine if a cell is black or white based on checkerboard pattern."""
        return 'black' if (i + j) % 2 == 0 else 'white'
    
    def domino_direction(self, domino: Domino) -> str:
        """Get the direction code (E/N/W/S) for a domino based on Wikipedia coloring."""
        (i1, j1), (i2, j2) = tuple(domino)
        if self.cell_parity(i1, j1) == 'black':
            b = (i1, j1)
            w = (i2, j2)
        else:
            b = (i2, j2) 
            w = (i1, j1)
        
        di = w[0] - b[0]
        dj = w[1] - b[1]
        
        if di == 1 and dj == 0:
            return 'E'  # East
        if di == -1 and dj == 0:
            return 'W'  # West
        if di == 0 and dj == 1:
            return 'N'  # North
        if di == 0 and dj == -1:
            return 'S'  # South
        raise ValueError("Invalid domino")
    
    def direction_to_flet_color(self, direction: str):
        """Convert direction code to Flet color."""
        color_map = {
            'E': ft.Colors.YELLOW_600,      # East - Yellow
            'N': ft.Colors.GREEN_600,       # North - Green  
            'W': ft.Colors.BLUE_600,        # West - Blue
            'S': ft.Colors.RED_600,         # South - Red
        }
        return color_map.get(direction, ft.Colors.GREY_600)
    
    def get_domino_bounds(self, domino: Domino, cell_size: float = 30):
        """Get the bounding rectangle for a domino."""
        (i1, j1), (i2, j2) = tuple(domino)
        
        if i1 == i2:  # Vertical domino
            x = i1 * cell_size
            y = min(j1, j2) * cell_size
            width = cell_size
            height = 2 * cell_size
        else:  # Horizontal domino
            x = min(i1, i2) * cell_size
            y = j1 * cell_size
            width = 2 * cell_size
            height = cell_size
            
        return x, y, width, height

    def flet_display(self, state):
        """Create a Flet display for the Aztec Diamond tiling with proper geometric visualization."""
        
        tiling = self.state_to_tiling(state)
        
        # Calculate bounds of the diamond
        xs = [i for i, _ in self.cells]
        ys = [j for _, j in self.cells] 
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        
        cell_size = 25  # Size of each unit cell in pixels
        
        # Create a stack to layer the dominoes
        domino_containers = []
        
        # Center the diamond in the display
        offset_x = -xmin * cell_size + 50
        offset_y = -ymin * cell_size + 50
        
        for domino in tiling:
            direction = self.domino_direction(domino)
            color = self.direction_to_flet_color(direction)
            
            x, y, width, height = self.get_domino_bounds(domino, cell_size)
            
            # Create domino rectangle
            domino_rect = ft.Container(
                width=width,
                height=height,
                bgcolor=color,
                border=ft.border.all(2, ft.Colors.BLACK),
                border_radius=3,
                left=x + offset_x,
                top=y + offset_y,
                tooltip=f"Domino {direction} at {tuple(domino)}"
            )
            domino_containers.append(domino_rect)
        
        # Calculate canvas size
        canvas_width = (xmax - xmin + 2) * cell_size + 100
        canvas_height = (ymax - ymin + 2) * cell_size + 100
        
        # Create the tiling visualization
        tiling_canvas = ft.Stack(
            controls=domino_containers,
            width=canvas_width,
            height=canvas_height
        )
        
        # Add info panel
        vertical_count = self.count_vertical_dominoes(tiling)
        horizontal_count = len(tiling) - vertical_count
        flippable_count = len(self.find_flippable(tiling))
        
        info_panel = ft.Column([
            ft.Text(f"Aztec Diamond (n={self.n})", 
                    size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text(f"Dominoes: {len(tiling)}", 
                    size=12, color=ft.Colors.WHITE70),
            ft.Text(f"Vertical: {vertical_count}, Horizontal: {horizontal_count}", 
                    size=12, color=ft.Colors.WHITE70),
            ft.Text(f"Flippable: {flippable_count}", 
                    size=12, color=ft.Colors.WHITE70),
            ft.Divider(color=ft.Colors.WHITE30, height=1),
            ft.Text("Colors:", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Row([
                ft.Container(width=15, height=15, bgcolor=ft.Colors.YELLOW_600, border_radius=2),
                ft.Text("E", size=10, color=ft.Colors.WHITE70),
                ft.Container(width=15, height=15, bgcolor=ft.Colors.GREEN_600, border_radius=2),
                ft.Text("N", size=10, color=ft.Colors.WHITE70),
                ft.Container(width=15, height=15, bgcolor=ft.Colors.BLUE_600, border_radius=2),
                ft.Text("W", size=10, color=ft.Colors.WHITE70),
                ft.Container(width=15, height=15, bgcolor=ft.Colors.RED_600, border_radius=2),
                ft.Text("S", size=10, color=ft.Colors.WHITE70),
            ], spacing=5)
        ], spacing=5)
        
        # Combine visualization and info
        display_content = ft.Row([
            ft.Container(
                content=tiling_canvas,
                bgcolor=ft.Colors.WHITE,
                border_radius=5,
                padding=10
            ),
            ft.Container(
                content=info_panel,
                bgcolor=ft.Colors.BLUE_GREY_800,
                border_radius=5,
                padding=15,
                width=180
            )
        ], spacing=10)
        
        return ft.Container(
            content=display_content,
            padding=10,
            bgcolor=ft.Colors.GREY_100,
            border_radius=10,
            alignment=ft.alignment.center
        )

    def create_interactive_board_display(self, state, visualizer=None):
        """Create an interactive board display for tile selection."""
        
        tiling = self.state_to_tiling(state)
        
        # Create a mapping from cell positions to dominoes
        cell_to_domino = {}
        for domino in tiling:
            (i1, j1), (i2, j2) = tuple(domino)
            cell_to_domino[(i1, j1)] = domino
            cell_to_domino[(i2, j2)] = domino
        
        # Calculate bounds of the diamond
        xs = [i for i, _ in self.cells]
        ys = [j for _, j in self.cells] 
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        
        # Create tile buttons grid
        tile_buttons = []
        
        for row in range(ymin, ymax + 1):
            button_row = []
            for col in range(xmin, xmax + 1):
                pos = (col, row)  # Note: using (col, row) to match coordinate system
                
                # Check if this position is within the diamond
                if pos in self.cells:
                    # Get the domino at this position
                    domino = cell_to_domino.get(pos)
                    
                    # Determine if this tile is selected
                    is_selected = pos in self.selected_tiles
                    
                    # Get direction for color coding
                    try:
                        direction = self.domino_direction(domino) if domino else '?'
                        color = self.direction_to_flet_color(direction)
                    except:
                        direction = '?'
                        color = ft.Colors.GREY_400
                    
                    # Create button for this tile
                    button = ft.ElevatedButton(
                        text=direction,
                        width=30,
                        height=30,
                        bgcolor=ft.Colors.RED_300 if is_selected else color,
                        color=ft.Colors.WHITE,
                        on_click=lambda e, p=pos: self.handle_tile_click(p, visualizer) if visualizer else None
                    )
                    button_row.append(button)
                else:
                    # Empty space outside diamond
                    button_row.append(ft.Container(width=30, height=30))
            
            tile_buttons.append(ft.Row(button_row, spacing=1, alignment=ft.MainAxisAlignment.CENTER))
        
        # Add selection info and controls
        selection_info = ft.Column([
            ft.Text(f"Selected: {len(self.selected_tiles)}/2", size=12, color=ft.Colors.WHITE),
            ft.Text(f"Tiles: {self.selected_tiles}" if self.selected_tiles else "Click tiles to select", 
                    size=10, color=ft.Colors.WHITE70),
            ft.Row([
                ft.ElevatedButton(
                    "Clear", 
                    on_click=lambda e: self.handle_clear_selection(visualizer) if visualizer else None,
                    width=80,
                    height=30,
                    bgcolor=ft.Colors.ORANGE_400
                ),
                ft.ElevatedButton(
                    "Flip",
                    on_click=lambda e: self.handle_flip_selected(visualizer) if visualizer else None,
                    disabled=len(self.selected_tiles) != 2,
                    width=80,
                    height=30,
                    bgcolor=ft.Colors.GREEN_400
                )
            ], spacing=10)
        ], spacing=5)
        
        return ft.Column([
            ft.Text("Select 2 tiles to flip:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Column(tile_buttons, spacing=1),
            selection_info
        ], spacing=10)

    def handle_tile_click(self, position, visualizer):
        """Handle tile click with visualizer update."""
        self.on_tile_click(position)
        if visualizer and hasattr(visualizer, 'update_interactive_board'):
            visualizer.update_interactive_board()

    def handle_clear_selection(self, visualizer):
        """Handle clear selection with visualizer update."""
        self.clear_tile_selection()
        if visualizer and hasattr(visualizer, 'update_interactive_board'):
            visualizer.update_interactive_board()

    def handle_flip_selected(self, visualizer):
        """Handle flip selected tiles with visualizer update."""
        if visualizer:
            current_state = visualizer.displayed_board[0]
            new_state, success = self.flip_selected_tiles(current_state)
            if success:
                # Update the visualizer with the new state
                visualizer.displayed_board[0] = new_state
                visualizer.update_game_board_display()
                visualizer.update_interactive_board()
                visualizer.update_next_states_dropdown()
