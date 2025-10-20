from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from typing import FrozenSet

import numpy as np
import flet as ft

from .game import Game, GameButton


@dataclass(frozen=True)
class Block:
    """A sliding block with multiple points and a color identifier."""
    points: tuple  # Tuple of (x, y) coordinates
    color: str = 'gray'
    piece_id: int = 0  # Unique identifier for the piece

class Klotski(Game):
    """
    Klotski sliding block puzzle implementation for state space visualization.
    
    This game represents the classic Klotski sliding block puzzle where players
    slide rectangular blocks of different sizes within a confined space to reach
    a goal configuration. The state space shows all possible block arrangements
    and legal sliding moves between them.

    There are three puzzle types available:
    - "Original Klotski": The classic 5x4 Klotski layout with a 2x2 target block.
    - "Medium Test": A smaller 5x3 layout for testing purposes.
    - "Small Test": A minimal 3x2 layout for quick testing.

    Example usage:
    ```
    def main(page: ft.Page):
        game = Klotski(puzzle_type="Original Klotski")
        visualizer = FletStateSpaceVisualizer(ALL_STATES=False)
        visualizer.build_ui(page, game)
    ft.app(target=main)
    ```
        
    """
    
    def __init__(self, puzzle_type="Original Klotski"):
        """
        Args:
            puzzle_type (str): Type of Klotski puzzle layout. Default is "Original Klotski".
        """
        super().__init__()
        self.puzzle_type = puzzle_type
        
        # Initialize puzzle based on type
        self._setup_puzzle()
        
        # Create piece-specific movement combinations
        self.button_names = []
        self.button_dirs = []
        self._create_piece_buttons()
        self.colorbar_title = "Distance to Goal"
        self.ignore_leaves = False
    
    def _setup_puzzle(self):
        """Set up puzzle configuration based on puzzle type."""
        if self.puzzle_type == "Original Klotski":
            self.width = 4
            self.height = 5
            self.region = {(x,y) for x in range(self.width) for y in range(self.height)}
            
            # Standard Klotski layout - piece IDs match expected positions exactly
            # Expected: [[ 1 10 10  2]
            #           [ 5 10 10  7]  
            #           [ 5  9  9  7]
            #           [ 6  2  3  8]
            #           [ 6  0  0  8]]
            self.start_config = frozenset([
                Block(((0,0),), 'purple', 1),                  # Position (0,0) → piece 1  
                Block(((1,3),), 'purple', 2),                  # Position (1,3) → piece 2 (where expected layout wants piece 2)
                Block(((2,3),), 'purple', 3),                  # Position (2,3) → piece 3
                Block(((3,0),), 'purple', 4),                  # Position (3,0) → piece 4 (where expected layout wants piece 2 but we use 4) 
                Block(((0,1),(0,2)), 'blue', 5),               # Positions (0,1),(0,2) → piece 5
                Block(((0,3),(0,4)), 'blue', 6),               # Positions (0,3),(0,4) → piece 6  
                Block(((3,1),(3,2)), 'blue', 7),               # Positions (3,1),(3,2) → piece 7
                Block(((3,3),(3,4)), 'blue', 8),               # Positions (3,3),(3,4) → piece 8
                Block(((1,2),(2,2)), 'darkgreen', 9),          # Positions (1,2),(2,2) → piece 9
                Block(((1,0),(2,0),(1,1),(2,1)), 'red', 10),   # Positions (1,0),(2,0),(1,1),(2,1) → piece 10
            ])
            
            self.goal_block = Block(((1,0),(2,0),(1,1),(2,1)), 'red', 10)
            
        elif self.puzzle_type == "Medium Test":
            # Correct Medium Test from notebook - should have ~58 configurations according to notebook
            self.width = 5
            self.height = 3
            self.region = {(x,y) for x in range(self.width) for y in range(self.height)}
            
            self.start_config = frozenset([
                Block(((0,0),(1,0),(2,0)), 'red', 1),           # 3-block horizontal target piece
                Block(((0,1),(1,1)), 'blue', 2),                # 2-block blue piece
                Block(((3,0),(4,0),(3,1),(4,1)), 'darkgreen', 3) # 2x2 green block
            ])
            
            self.goal_block = Block(((2,2),(3,2),(4,2)), 'red', 1)  # Goal: red piece at bottom
            
        elif self.puzzle_type == "Small Test":
            self.width = 3
            self.height = 2
            self.region = {(x,y) for x in range(self.width) for y in range(self.height)}
            
            self.start_config = frozenset([
                Block(((1,0),(2,0)), 'red', 1),  # Target piece
                Block(((0,0),), 'blue', 2),
                Block(((2,1),), 'blue', 3)
            ])
            
            self.goal_block = Block(((0,1),(1,1)), 'red', 1)
        
        else:
            # Default to Medium Test if no match
            self.width = 5
            self.height = 3
            self.region = {(x,y) for x in range(self.width) for y in range(self.height)}
            
            self.start_config = frozenset([
                Block(((0,0),(1,0),(2,0)), 'red', 1),           # 3-block horizontal target piece
                Block(((0,1),(1,1)), 'blue', 2),                # 2-block blue piece
                Block(((3,0),(4,0),(3,1),(4,1)), 'darkgreen', 3) # 2x2 green block
            ])
            
            self.goal_block = Block(((2,2),(3,2),(4,2)), 'red', 1)  # Goal: red piece at bottom
        
        # Set up grid dimensions for compatibility
        self.SHAPE = (self.height, self.width)
        self.n, self.m = self.SHAPE
        
        # Movement directions
        self.moves = [(0,1), (0,-1), (1,0), (-1,0)]  # right, left, down, up
        
        # Set up goal position (top-left corner of goal block)
        self.goal_position = (min(y for x, y in self.goal_block.points), 
                             min(x for x, y in self.goal_block.points))
        
        # Extract piece IDs from the initial configuration
        self.pieces = [block.piece_id for block in self.start_config]
    
    def translate_block(self, tile: Block, move: tuple) -> Block:
        """Translate a block by a given move."""
        return Block(tuple((point[0]+move[0], point[1]+move[1]) for point in tile.points), tile.color, tile.piece_id)
    
    def get_neighbors(self, cfg):
        """Get all valid neighbor configurations from the current config."""
        all_points = set()
        for block in cfg:
            for point in block.points:
                all_points.add(point)
        for tile in cfg:
            for move in self.moves:
                legal_move = True
                for point in tile.points:
                    translated_point = (point[0] + move[0], point[1] + move[1])
                    if translated_point not in self.region or (translated_point in all_points and translated_point not in tile.points):
                        legal_move = False
                        break
                if legal_move:
                    yield cfg.symmetric_difference(set((tile, self.translate_block(tile, move))))
    
    def config_to_state(self, config):
        """Convert a configuration to a state tuple for compatibility."""
        # Create a grid representation for visualization compatibility
        grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        for block in config:
            for point in block.points:
                x, y = point
                if 0 <= x < self.width and 0 <= y < self.height:
                    grid[y][x] = block.piece_id
        
        # Flatten to tuple
        return tuple(tuple(row) for row in grid)
    
    def state_to_config(self, state):
        """Convert a state tuple back to a configuration."""
        # Handle different state formats
        if isinstance(state, (list, tuple)) and len(state) > 0:
            if isinstance(state[0], (list, tuple)):
                # Nested format: ((a,b,c), (d,e,f), ...)
                grid = state
            else:
                # Flat format: (a,b,c,d,e,f,...)
                # Convert to nested
                grid = []
                for y in range(self.height):
                    row = []
                    for x in range(self.width):
                        idx = y * self.width + x
                        if idx < len(state):
                            row.append(state[idx])
                        else:
                            row.append(0)
                    grid.append(row)
        else:
            # Invalid state, create empty grid
            grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Group points by piece_id
        piece_points = {}
        piece_colors = {}
        
        for y in range(self.height):
            for x in range(self.width):
                if y < len(grid) and x < len(grid[y]):
                    piece_id = grid[y][x]
                    if piece_id != 0:
                        if piece_id not in piece_points:
                            piece_points[piece_id] = []
                            # Assign colors based on piece_id
                            if piece_id == 1:
                                piece_colors[piece_id] = 'red'  # Target piece
                            elif piece_id <= 4:
                                piece_colors[piece_id] = 'purple'
                            elif piece_id <= 8:
                                piece_colors[piece_id] = 'blue'
                            else:
                                piece_colors[piece_id] = 'darkgreen'
                        
                        piece_points[piece_id].append((x, y))
        
        # Create blocks
        blocks = []
        for piece_id, points in piece_points.items():
            color = piece_colors.get(piece_id, 'gray')
            blocks.append(Block(tuple(points), color, piece_id))
        
        return frozenset(blocks)
    
    def get_pieces_on_board(self, state):
        """Get a list of piece IDs that are actually present in the configuration."""
        config = self.state_to_config(state)
        return sorted([block.piece_id for block in config])
    
    def get_initial_layout(self):
        """Get the initial configuration as a state tuple."""
        return self.config_to_state(self.start_config)
    
    def state_to_board(self, state):
        """Convert state tuple to 2D numpy array for compatibility."""
        board = np.zeros((self.height, self.width), dtype=int)
        
        # Handle different state formats
        if isinstance(state, (list, tuple)) and len(state) > 0:
            if isinstance(state[0], (list, tuple)):
                # Nested format: ((a,b,c), (d,e,f), ...)
                for y in range(min(self.height, len(state))):
                    for x in range(min(self.width, len(state[y]))):
                        board[y][x] = state[y][x]
            else:
                # Flat format: (a,b,c,d,e,f,...)
                for y in range(self.height):
                    for x in range(self.width):
                        idx = y * self.width + x
                        if idx < len(state):
                            board[y][x] = state[idx]
        
        return board
    
    def board_to_state(self, board):
        """Convert 2D numpy array back to state tuple."""
        return tuple(tuple(row) for row in board.tolist())
    
    def is_solved(self, state):
        """Check if the puzzle is solved (target block at goal position)."""
        config = self.state_to_config(state)
        return self.goal_block in config
    
    def can_move_piece(self, board, piece_id, direction):
        """Check if a specific piece can move in the given direction."""
        # Convert to configuration and check if move is valid
        state = self.board_to_state(board)
        config = self.state_to_config(state)
        
        # Find the block with the given piece_id
        target_block = None
        for block in config:
            if block.piece_id == piece_id:
                target_block = block
                break
        
        if target_block is None:
            return False
        
        # Get all occupied points
        all_points = set()
        for block in config:
            for point in block.points:
                all_points.add(point)
        
        # Check if the move is valid for this block
        move = self.moves[direction]
        for point in target_block.points:
            translated_point = (point[0] + move[0], point[1] + move[1])
            if (translated_point not in self.region or 
                (translated_point in all_points and translated_point not in target_block.points)):
                return False
        
        return True
    
    def move_piece(self, board, piece_id, direction):
        """Move a specific piece in the given direction."""
        if not self.can_move_piece(board, piece_id, direction):
            return board, False
        
        # Convert to configuration
        state = self.board_to_state(board)
        config = self.state_to_config(state)
        
        # Find and move the target block
        target_block = None
        for block in config:
            if block.piece_id == piece_id:
                target_block = block
                break
        
        if target_block is None:
            return board, False
        
        # Create new configuration with moved block
        move = self.moves[direction]
        new_block = self.translate_block(target_block, move)
        new_config = config.symmetric_difference({target_block, new_block})
        
        # Convert back to board
        new_state = self.config_to_state(frozenset(new_config))
        new_board = self.state_to_board(new_state)
        
        return new_board, True

    def move(self, state, encoded_direction):
        """Move a specific piece in the given direction using encoded direction."""
        # Decode piece_id and direction from encoded value
        # print(state, encoded_direction)
        piece_id = encoded_direction // 100
        direction = encoded_direction % 100
        
        return self.move_specific_piece(state, piece_id, direction)
    
    def move_specific_piece(self, state, piece_id, direction):
        """Move a specific piece in the given direction."""
        board = self.state_to_board(state)
        
        if self.can_move_piece(board, piece_id, direction):
            new_board, changed = self.move_piece(board, piece_id, direction)
            if changed:
                return self.board_to_state(new_board), True
        
        return state, False
    
    def manhattan_distance_to_goal(self, state):
        """Calculate distance metric for the puzzle state."""
        config = self.state_to_config(state)
        
        # Find target piece (piece_id=1 for most puzzles)
        target_piece_id = 1
        target_block = None
        for block in config:
            if block.piece_id == target_piece_id:
                target_block = block
                break
        
        if target_block is None:
            return 10  # Default distance if target not found
        
        # Calculate distance between current position and goal
        # Use center of mass for multi-point blocks
        current_center = (
            sum(p[0] for p in target_block.points) / len(target_block.points),
            sum(p[1] for p in target_block.points) / len(target_block.points)
        )
        
        goal_center = (
            sum(p[0] for p in self.goal_block.points) / len(self.goal_block.points),
            sum(p[1] for p in self.goal_block.points) / len(self.goal_block.points)
        )
        
        return abs(current_center[0] - goal_center[0]) + abs(current_center[1] - goal_center[1])
    
    def board_score(self, state):
        """Score based on negative distance to goal (higher = better)."""
        if self.is_solved(state):
            return 1000  # High score for solved state
        
        distance = self.manhattan_distance_to_goal(state)
        return -distance
    
    def canonical(self, state):
        """Return canonical form of state (no symmetries for Klotski)."""
        return state
    
    def expected_score(self, state):
        """Expected score heuristic."""
        return self.board_score(state)
    
    def spawn_children(self, state):
        """Klotski is deterministic - no randomness."""
        return [(state, 1.0)]

    def _create_piece_buttons(self, state=None):
        """Create button names and directions for pieces present on the board."""
        # Clear existing buttons
        self.button_names = []
        self.button_dirs = []
        
        # If no state provided, use initial layout
        if state is None:
            state = self.get_initial_layout()
        
        # Get pieces actually present on the board
        active_pieces = self.get_pieces_on_board(state)
        
        # Piece names for display with numbers
        piece_names = {
            1: "🎯1",      # Large 2x2 target piece
            2: "📏2",     # Tall piece 1
            3: "📏3",     # Tall piece 2
            4: "📏4",     # Tall piece 3
            5: "📏5",     # Tall piece 4
            6: "➡️6",     # Wide piece
            7: "🔸7",      # Small piece 1
            8: "🔸8",      # Small piece 2
            9: "🔸9",      # Small piece 3
            10: "🔸10",    # Small piece 4
            11: "🏢11",  # Custom tall piece
            12: "📐12",  # Custom wide piece
        }
        
        # Direction symbols and names
        dir_symbols = ["⬆️", "⬇️", "⬅️", "➡️"]
        dir_names = ["Up", "Down", "Left", "Right"]
        
        # Create buttons only for pieces that are actually on the board
        for piece_id in active_pieces:
            piece_name = piece_names.get(piece_id, f"P{piece_id}")
            
            for direction in range(4):  # 0=Up, 1=Down, 2=Left, 3=Right
                symbol = dir_symbols[direction]
                dir_name = dir_names[direction]
                
                # Create button name
                button_name = f"{piece_name} {symbol}"
                self.button_names.append(button_name)
                
                # Encode piece_id and direction into a single value
                # Use formula: button_dir = piece_id * 100 + direction
                # This allows us to decode: piece_id = button_dir // 100, direction = button_dir % 100
                button_dir = piece_id * 100 + direction
                self.button_dirs.append(button_dir)

    # def get_initial_layout(self):
    #     """Get the initial board layout for classic Klotski."""
    #     # Create empty 5x4 board
    #     board = np.zeros((5, 4), dtype=int)
        
    #     # Classic Klotski starting position
    #     # Row 0: [2][1][1][3]  (tall pieces 2,3 around large piece 1)
    #     # Row 1: [2][1][1][3]
    #     # Row 2: [4][6][6][5]  (tall pieces 4,5 around wide piece 6)
    #     # Row 3: [4][7][8][5]  (small pieces 7,8 in middle)
    #     # Row 4: [9][ ][10][ ] (small pieces 9,10 with empty spaces)
        
    #     # Place large piece (1) at top center
    #     board[0:2, 1:3] = 1
        
    #     # Place tall pieces
    #     board[0:2, 0] = 2  # Left tall piece
    #     board[0:2, 3] = 3  # Right tall piece
    #     board[2:4, 0] = 4  # Bottom left tall piece
    #     board[2:4, 3] = 5  # Bottom right tall piece
        
    #     # Place wide piece
    #     board[2, 1:3] = 6
        
    #     # Place small pieces
    #     board[3, 1] = 7   # Small piece 1
    #     board[3, 2] = 8   # Small piece 2
    #     board[4, 0] = 9   # Small piece 3
    #     board[4, 2] = 10  # Small piece 4
        
    #     # Positions (4,1) and (4,3) remain empty (0)
        
    #     return tuple(board.flatten())

    def create_game_buttons(self, visualizer):
        """Create piece-specific buttons for Klotski puzzle."""
        
        # Create move buttons using the button_names and button_dirs
        move_buttons = []
        for direction, name in zip(self.button_dirs, self.button_names):
            # Decode piece and direction to check if move is possible
            piece_id = direction // 100
            actual_direction = direction % 100
            
            # Check if this move is currently possible
            initial_state = self.get_initial_layout()
            board = self.state_to_board(initial_state)
            can_move = self.can_move_piece(board, piece_id, actual_direction)
            
            # Use different colors for enabled vs disabled buttons
            if can_move:
                bgcolor = ft.Colors.GREEN_600  # Green for clickable moves
                color = ft.Colors.WHITE
            else:
                bgcolor = ft.Colors.BLUE_GREY_800  # Grey for blocked moves
                color = ft.Colors.WHITE70      # Dimmed text for disabled
            
            button = GameButton(
                text=name,
                on_click_fn=lambda e, d=direction: visualizer.on_move_button_click(d)(e),
                width=120,
                height=40,
                bgcolor=bgcolor,
                color=color
            )
            
            # Set initial enabled state
            button.set_enabled(can_move)
            move_buttons.append(button)
        
        # Create control buttons
        restart_button = GameButton(
            text=self.get_restart_desc(),
            on_click_fn=visualizer.on_restart_button_click,
            bgcolor=ft.Colors.BLUE_400,
            color=ft.Colors.WHITE,
            width=200
        )
        
        luck_button = GameButton(
            text="Luck: OFF",
            on_click_fn=visualizer.on_luck_button_click,
            bgcolor=ft.Colors.ORANGE_300,
            color=ft.Colors.WHITE
        )
        
        return {
            'move': move_buttons,
            'control': [restart_button, luck_button]
        }

    def update_button_states(self, state, move_buttons):
        """Update the visual state of buttons based on current game state."""
        
        board = self.state_to_board(state)
        
        for i, button in enumerate(move_buttons):
            # Get the encoded direction for this button
            direction = self.button_dirs[i]
            piece_id = direction // 100
            actual_direction = direction % 100
            
            # Check if this move is currently possible
            can_move = self.can_move_piece(board, piece_id, actual_direction)
            
            # Update button state and appearance
            button.set_enabled(can_move)
            
            # Update button colors to reflect state
            if button._flet_button:
                if can_move:
                    button._flet_button.bgcolor = ft.Colors.GREEN_600  # Green for clickable
                    button._flet_button.color = ft.Colors.WHITE
                else:
                    button._flet_button.bgcolor = ft.Colors.BLUE_GREY_800    # Red for blocked
                    button._flet_button.color = ft.Colors.WHITE70
                button._flet_button.update()

    def update_buttons_for_state(self, state):
        """Update button configuration based on current state."""
        # Get pieces on the current board
        current_pieces = set(self.get_pieces_on_board(state))
        
        # Get pieces from current button configuration
        current_button_pieces = set()
        for button_dir in self.button_dirs:
            piece_id = button_dir // 100
            current_button_pieces.add(piece_id)
        
        # If pieces have changed, recreate buttons
        if current_pieces != current_button_pieces:
            self._create_piece_buttons(state)
            return True  # Buttons were updated
        return False  # No update needed

    def move_specific_piece(self, state, piece_id, direction):
        """Move a specific piece in the given direction."""
        board = self.state_to_board(state)
        
        if self.can_move_piece(board, piece_id, direction):
            new_board, changed = self.move_piece(board, piece_id, direction)
            if changed:
                return self.board_to_state(new_board), True
        
        return state, False

    def find_piece_positions(self, state):
        """Find positions of all pieces on the board."""
        board = self.state_to_board(state)
        piece_positions = {}
        
        for piece_id in self.pieces:
            positions = np.where(board == piece_id)
            if len(positions[0]) > 0:
                # Get top-left corner of the piece
                min_row, min_col = int(positions[0].min()), int(positions[1].min())
                piece_positions[piece_id] = (min_row, min_col)
        
        return piece_positions

    def can_move_piece(self, board, piece_id, direction):
        """Check if a piece can move in the given direction using Block-based logic."""
        if piece_id not in self.pieces:
            return False
            
        # Get current configuration from board
        current_config = self.state_to_config(self.board_to_state(board))
        
        # Find the block with this piece_id
        target_block = None
        for block in current_config:
            if block.piece_id == piece_id:
                target_block = block
                break
                
        if target_block is None:
            return False
            
        # Get the move vector
        move_vectors = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Up, Down, Left, Right
        if direction < 0 or direction >= len(move_vectors):
            return False
            
        move = move_vectors[direction]
        
        # Check if the move is legal (similar to get_neighbors logic)
        all_points = set()
        for block in current_config:
            for point in block.points:
                all_points.add(point)
        
        # Check if all translated points would be legal
        for point in target_block.points:
            translated_point = (point[0] + move[0], point[1] + move[1])
            if (translated_point not in self.region or 
                (translated_point in all_points and translated_point not in target_block.points)):
                return False
        
        return True

    def move_piece(self, board, piece_id, direction):
        """Move a piece in the given direction using Block-based logic."""
        if not self.can_move_piece(board, piece_id, direction):
            return board, False
            
        # Get current configuration from board
        current_config = self.state_to_config(self.board_to_state(board))
        
        # Find the block with this piece_id
        target_block = None
        for block in current_config:
            if block.piece_id == piece_id:
                target_block = block
                break
                
        if target_block is None:
            return board, False
            
        # Get the move vector
        move_vectors = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Up, Down, Left, Right
        if direction < 0 or direction >= len(move_vectors):
            return board, False
            
        move = move_vectors[direction]
        
        # Create new configuration with moved block
        new_config = current_config.symmetric_difference({target_block, self.translate_block(target_block, move)})
        
        # Convert back to board
        new_state = self.config_to_state(frozenset(new_config))
        new_board = self.state_to_board(new_state)
                
        return new_board, True

    def move(self, state, encoded_direction):
        """Move a specific piece in the given direction."""
        # Decode piece_id and direction from encoded value
        piece_id = encoded_direction // 100
        direction = encoded_direction % 100
        
        return self.move_specific_piece(state, piece_id, direction)

    def spawn_children(self, state):
        """Klotski is deterministic - no randomness."""
        return [(state, 1.0)]

    def is_solved(self, state):
        """Check if the puzzle is solved (large piece at goal position)."""
        board = self.state_to_board(state)
        target_row, target_col = self.goal_position
        
        # Check if the 2x2 large piece (piece 1) is at the goal position
        try:
            return (board[target_row, target_col] == 1 and
                    board[target_row, target_col + 1] == 1 and
                    board[target_row + 1, target_col] == 1 and
                    board[target_row + 1, target_col + 1] == 1)
        except IndexError:
            return False

    def manhattan_distance_to_goal(self, state):
        """Calculate Manhattan distance of target piece to goal position."""
        board = self.state_to_board(state)
        
        # Look for the target piece (piece ID 1, or fallback to most common piece)
        target_piece_id = 1
        piece_positions = np.where(board == target_piece_id)
        
        # If target piece not found, try to find a reasonable alternative
        if len(piece_positions[0]) == 0:
            # Find the most frequent piece (excluding 0)
            unique, counts = np.unique(board[board != 0], return_counts=True)
            if len(unique) > 0:
                # Use the piece with highest frequency as target
                target_piece_id = unique[np.argmax(counts)]
                piece_positions = np.where(board == target_piece_id)
        
        if len(piece_positions[0]) == 0:
            # No pieces found, return a reasonable default distance
            return 10  # Arbitrary reasonable distance
            
        # Get top-left corner of target piece
        current_row = int(piece_positions[0].min())
        current_col = int(piece_positions[1].min())
        
        # Calculate distance to goal position
        target_row, target_col = self.goal_position
        return abs(current_row - target_row) + abs(current_col - target_col)

    def board_score(self, state):
        """Score based on negative distance to goal (higher = better)."""
        if self.is_solved(state):
            return 1000  # High score for solved state
        
        distance = self.manhattan_distance_to_goal(state)
        # Ensure we don't return infinity values that cause JSON serialization issues
        if distance == float('inf') or distance != distance:  # NaN check
            return -100  # Reasonable penalty for invalid states
        return -distance

    def canonical(self, state):
        """For Klotski, return state as-is (no symmetries due to specific piece arrangement)."""
        return state

    @lru_cache(None)
    def expected_score(self, state):
        """Simple heuristic: negative Manhattan distance to goal."""
        return self.board_score(state)

    def enumerate_states(self, initial_tiles=None, ALL_STATES=False, ignore_leaves=False):
        """Enumerate reachable states using the notebook's approach."""
        # Use the start_config directly to avoid state conversion issues

        all_cfgs = {self.start_config}
        unvisited_configs = {self.start_config}
        print(self.start_config)
        while len(unvisited_configs) > 0:
            # print(len(unvisited_configs))
            config = unvisited_configs.pop()
            
            # Get neighbors using the notebook's method
            for neighbor_config in self.get_neighbors(config):
                if neighbor_config not in all_cfgs and neighbor_config not in unvisited_configs:
                    all_cfgs.add(neighbor_config)
                    unvisited_configs.add(neighbor_config)
        
        # Check if we hit the limit or found all configurations naturally
        if len(unvisited_configs) == 0:
            print(f"✅ Generated {len(all_cfgs)} reachable configurations (complete enumeration)")
        else:
            print(f"⚠️  Generated {len(all_cfgs)} reachable configurations (hit limit, {len(unvisited_configs)} unvisited remaining)")
        
        # Convert configurations to states and build edges
        states = []
        config_to_idx = {}
        
        for i, config in enumerate(all_cfgs):
            state = self.config_to_state(config)
            states.append(state)
            config_to_idx[config] = i
            
        print(f"✅ Converted {len(states)} configurations to states")
        
        # Build edges
        edges = defaultdict(float)
        print(f"🔗 Computing edges for {len(all_cfgs)} configurations...")
        
        for config in all_cfgs:
            state = self.config_to_state(config)
            neighbors = self.get_neighbors(config)
            
            for neighbor_config in neighbors:
                if neighbor_config in config_to_idx:
                    u_idx = config_to_idx[config]
                    v_idx = config_to_idx[neighbor_config]
                    edges[(u_idx, v_idx)] = 1

        print(f"� Generated {len(edges)} edges")
        
        # Convert to nodes and edge lists
        nodes = states
        edges_w = [(u_idx, v_idx, w) for (u_idx, v_idx), w in edges.items()]

        labels = {}
        for i, state in enumerate(nodes):
            labels[i] = {
                'state': state,
                'expected_score': self.expected_score(state),
            }
        
        return nodes, edges_w, labels

    def state_scalar(self, state):
        """Return negative Manhattan distance for coloring."""
        return self.manhattan_distance_to_goal(state)

    def board_to_display(self, state):
        """Return string representation of the board."""
        board = self.state_to_board(state)
        return str(board.tolist())

    def board_annotations(self, board):
        """Return annotations for displaying the puzzle."""
        anns = []
        n, m = board.shape
        
        for i in range(n):
            for j in range(m):
                val = int(board[i, j])
                if val == 0:
                    text = '·'
                    color = 'lightgray'
                elif val == 1:
                    text = str(val)
                    color = 'red'  # Target piece in red
                else:
                    text = str(val)
                    color = 'blue'
                    
                anns.append(dict(
                    x=j, y=n-1-i, text=text, 
                    xanchor='center', yanchor='middle', 
                    showarrow=False, 
                    font=dict(color=color, size=20)
                ))
        return anns

    def initial_state(self, nodes, edges_w, labels):
        """For Klotski, initial state is the classic starting layout."""
        initial_state = self.get_initial_layout()
        initial_state_canonical = self.canonical(initial_state)
        state_to_idx = {labels[j]['state']: j for j in range(len(labels))}
        return state_to_idx.get(initial_state_canonical, 0)

    def get_restart_desc(self):
        """Return restart button description for Klotski."""
        return "Restart (Initial Layout)"

    def flet_display(self, state):
        """Create a Flet display for the Klotski puzzle board."""
        
        board = self.state_to_board(state)
        h, w = board.shape
        
        # Create grid container
        board_container = ft.Column(spacing=2, alignment=ft.MainAxisAlignment.CENTER)
        
        # Color mapping for different pieces
        piece_colors = {
            0: ft.Colors.GREY_200,      # Empty space
            1: ft.Colors.RED_400,       # Big piece (usually the main piece to move)
            2: ft.Colors.BLUE_400,      # Medium pieces
            3: ft.Colors.GREEN_400,     # Other pieces
            4: ft.Colors.ORANGE_400,    # Other pieces
            5: ft.Colors.PURPLE_400,    # Other pieces
            6: ft.Colors.YELLOW_400,    # Other pieces
            7: ft.Colors.PINK_400,      # Other pieces
            8: ft.Colors.CYAN_400,      # Other pieces
            9: ft.Colors.BROWN_400,     # Other pieces
            10: ft.Colors.INDIGO_400,   # Other pieces
        }
        
        for i in range(h):
            row_controls = []
            for j in range(w):
                cell_value = int(board[i, j])
                
                if cell_value == 0:
                    # Empty space
                    cell_container = ft.Container(
                        content=ft.Text("", text_align=ft.TextAlign.CENTER),
                        width=40,
                        height=40,
                        bgcolor=piece_colors.get(cell_value, ft.Colors.GREY_200),
                        border_radius=3,
                        alignment=ft.alignment.center,
                        border=ft.border.all(1, ft.Colors.GREY_400)
                    )
                else:
                    # Piece
                    cell_container = ft.Container(
                        content=ft.Text(
                            str(cell_value),
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER
                        ),
                        width=40,
                        height=40,
                        bgcolor=piece_colors.get(cell_value, ft.Colors.GREY_600),
                        border_radius=3,
                        alignment=ft.alignment.center,
                        border=ft.border.all(1, ft.Colors.BLACK)
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
