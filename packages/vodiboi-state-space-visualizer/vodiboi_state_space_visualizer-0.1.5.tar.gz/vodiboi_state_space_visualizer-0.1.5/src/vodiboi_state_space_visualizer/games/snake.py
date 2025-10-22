import numpy as np
import flet as ft

from .game import Game, GameButton


class Snake(Game):
    """
    Snake game implementation for state space visualization.
    
    This game represents the classic Snake game where a snake moves around
    a grid eating apples and growing longer. The state space shows all possible
    snake configurations, apple positions, and movement transitions between them.

    Example usage:
    ```
    def main(page: ft.Page):
        game = Snake(SHAPE=(3, 3))
        visualizer = FletStateSpaceVisualizer()
        visualizer.build_ui(page, game)
    ft.app(target=main)
    ```
        
    """
    def __init__(self, SHAPE=(2, 2)):
        """
        Args:
            SHAPE (tuple): Grid dimensions as (rows, columns). Default is (2, 2).
        """
        super().__init__()
        self.SHAPE = SHAPE
        self.button_names = ['Up', 'Down', 'Left', 'Right']
        self.button_dirs = [0, 1, 2, 3]  # up, down, left, right
        self.colorbar_title = "Snake Length"
        self.ignore_leaves = False

    def get_snake_positions(self, state):
        """Extract snake positions from state.
        
        New State format: (snake_positions_tuple, apple_position_tuple)
        where snake_positions_tuple[0] is head, snake_positions_tuple[-1] is tail
        Returns: List of (row, col) positions from head to tail (preserving order)
        """
        snake_positions, apple_position = state
        return list(snake_positions)  # Convert tuple to list for compatibility

    def state_to_board(self, state):
        """Convert state to 2D board array.
        
        Board values: 0=empty, 1=snake_body, 2=snake_head, 3=apple
        """
        snake_positions, apple_position = state
        board = np.zeros(self.SHAPE, dtype=int)
        
        # Place apple (if valid position)
        if apple_position is not None:
            apple_row, apple_col = apple_position
            board[apple_row, apple_col] = 3
        
        # Place snake
        for i, (row, col) in enumerate(snake_positions):
            if i == 0:  # head (first element)
                board[row, col] = 2
            else:  # body segments
                board[row, col] = 1
                
        return board

    def board_to_state(self, board):
        """Convert board back to state (needed for some operations)."""
        # Find apple position
        apple_pos = np.where(board == 3)
        if len(apple_pos[0]) > 0:
            apple_position = (int(apple_pos[0][0]), int(apple_pos[1][0]))
        else:
            apple_position = None
        
        # Find snake positions
        snake_positions = []
        
        # Find head first
        head_pos = np.where(board == 2)
        if len(head_pos[0]) > 0:
            head_position = (int(head_pos[0][0]), int(head_pos[1][0]))
            snake_positions.append(head_position)
        
        # Find body segments
        body_positions = np.where(board == 1)
        for i in range(len(body_positions[0])):
            body_pos = (int(body_positions[0][i]), int(body_positions[1][i]))
            snake_positions.append(body_pos)
        
        return (tuple(snake_positions), apple_position)

    def move(self, state, direction):
        """Move snake in given direction.
        
        New implementation using direct position encoding.
        Returns: (new_state, changed)
        """
        snake_positions, apple_position = state
        
        if not snake_positions:
            return state, False
            
        head_row, head_col = snake_positions[0]  # Head is first element
        
        # Calculate new head position
        if direction == 0:  # up
            new_head_row, new_head_col = head_row - 1, head_col
        elif direction == 1:  # down
            new_head_row, new_head_col = head_row + 1, head_col
        elif direction == 2:  # left
            new_head_row, new_head_col = head_row, head_col - 1
        else:  # right
            new_head_row, new_head_col = head_row, head_col + 1
            
        new_head_pos = (new_head_row, new_head_col)
        
        # Check bounds
        if new_head_row < 0 or new_head_row >= self.SHAPE[0] or new_head_col < 0 or new_head_col >= self.SHAPE[1]:
            return state, False
            
        # Check if snake hits itself
        if new_head_pos in snake_positions:
            return state, False
            
        # Check if apple is eaten
        ate_apple = (new_head_pos == apple_position)
        
        if ate_apple:
            # Snake grows: add new head, keep all body segments
            new_snake_positions = tuple([new_head_pos] + list(snake_positions))
            
            # Check for win condition (snake fills entire grid)
            max_length = self.SHAPE[0] * self.SHAPE[1]
            if len(new_snake_positions) >= max_length:
                # Snake wins! No room for apple
                new_state = (new_snake_positions, None)
                return new_state, True
            
            # Return intermediate state without apple placement - spawn_children will handle this
            new_state = (new_snake_positions, None)
        else:
            # Normal move: add new head, remove tail (right shift)
            new_snake_positions = tuple([new_head_pos] + list(snake_positions[:-1]))
            new_state = (new_snake_positions, apple_position)
            
        return new_state, True

    def spawn_children(self, state):
        """Return all possible states after apple spawning when an apple was eaten."""
        snake_positions, apple_position = state
        
        # If apple is already placed, no spawning needed
        if apple_position is not None:
            return [(state, 1.0)]
        
        # If this is a win state (snake fills entire grid), no spawning
        max_length = self.SHAPE[0] * self.SHAPE[1]
        if len(snake_positions) >= max_length:
            return [(state, 1.0)]
        
        # Find all available positions for apple spawning
        available_positions = []
        for r in range(self.SHAPE[0]):
            for c in range(self.SHAPE[1]):
                if (r, c) not in snake_positions:
                    available_positions.append((r, c))
        
        if not available_positions:
            # No space for apple - this shouldn't happen in valid states
            return [(state, 1.0)]
        
        # Create child states with apple at each available position
        children = []
        prob_per_position = 1.0 / len(available_positions)
        
        for apple_pos in available_positions:
            child_state = (snake_positions, apple_pos)
            children.append((child_state, prob_per_position))
        
        return children

    def board_score(self, state):
        """Score based on snake length."""
        snake_positions, apple_position = state
        return len(snake_positions)

    def canonical(self, state):
        """Return canonical representation of state."""
        return state  # States are already canonical

    def expected_score(self, state):
        """Expected score is just the current score for deterministic game."""
        return self.board_score(state)

    def state_scalar(self, state):
        """Return scalar for coloring - use snake length."""
        snake_positions, apple_position = state
        return len(snake_positions)

    def board_to_display(self, state):
        """Return displayable string representation."""
        snake_positions, apple_position = state
        max_length = self.SHAPE[0] * self.SHAPE[1]
        length = len(snake_positions)
        
        if apple_position is None or length >= max_length:
            return f"Snake Len={length}, 🏆 WON! (Grid Full)"
        
        head_pos = snake_positions[0]
        return f"Snake@{head_pos}, Len={length}, Apple@{apple_position}"

    def board_annotations(self, board):
        """Return plotly annotations for board visualization."""
        annotations = []
        n, m = board.shape  # Grid dimensions
        for i in range(n):
            for j in range(m):
                val = board[i, j]
                symbol = ""
                color = "black"
                if val == 1:  # snake body/tail
                    symbol = "●"
                    color = "green"
                elif val == 2:  # snake head
                    symbol = "◉"
                    color = "darkgreen"
                elif val == 3:  # apple
                    symbol = "🍎"
                    color = "red"
                
                if symbol:
                    annotations.append(dict(
                        x=j, y=n-1-i,  # Use same coordinate system as other games
                        text=symbol,
                        xanchor='center', yanchor='middle', 
                        showarrow=False, 
                        font=dict(size=20, color=color)
                    ))
        return annotations

    def enumerate_states(self, ALL_STATES=True, ignore_leaves=False):
        """Generate states by exploration starting from initial state."""
        states = []
        state_to_idx = {}
        
        # Start with initial state: length-1 snake at (0,0), apple at bottom-right
        apple_pos = (self.SHAPE[0] - 1, self.SHAPE[1] - 1)
        initial_state = (((0, 0),), apple_pos)
        states.append(initial_state)
        state_to_idx[initial_state] = 0
        
        # For small grids, we can enumerate reachable states by exploration
        queue = [initial_state]
        visited = {initial_state}
        
        while queue:
            current_state = queue.pop(0)
            
            # Try all four move directions
            for direction in range(4):
                new_state, changed = self.move(current_state, direction)
                if changed:
                    # Handle probabilistic apple spawning
                    for child_state, prob in self.spawn_children(new_state):
                        if child_state not in visited:
                            visited.add(child_state)
                            states.append(child_state)
                            state_to_idx[child_state] = len(states) - 1
                            queue.append(child_state)
        
        # Generate transitions
        edges_w = []
        labels = {}
        
        # Create labels for all states first
        for i, state in enumerate(states):
            labels[i] = {
                'state': state,
                'score': self.board_score(state),
                'expected_score': self.expected_score(state),
                'display': self.board_to_display(state)
            }
        
        # Generate edges
        for i, state in enumerate(states):
            # Try each move direction
            for direction in range(4):
                new_state, changed = self.move(state, direction)
                if changed:
                    # Handle probabilistic apple spawning
                    for child_state, prob in self.spawn_children(new_state):
                        if child_state in state_to_idx:
                            j = state_to_idx[child_state]
                            edges_w.append((i, j, prob))
        
        return states, edges_w, labels

    def _is_connected_snake(self, snake_positions):
        """Check if snake positions form a connected sequence (each segment adjacent to next)."""
        if len(snake_positions) <= 1:
            return True
        
        for i in range(len(snake_positions) - 1):
            pos1 = snake_positions[i]
            pos2 = snake_positions[i + 1]
            # Check if adjacent (Manhattan distance = 1)
            if abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) != 1:
                return False
        return True

        # Generate transitions
        edges_w = []
        labels = {}
        
        # Create labels for all states first
        for i, state in enumerate(states):
            labels[i] = {
                'state': state,
                'score': self.board_score(state),
                'expected_score': self.expected_score(state),
                'display': self.board_to_display(state)
            }
        
        # Process states iteratively to handle dynamically added states
        i = 0
        while i < len(states):
            state = states[i]
            
            # Try each move direction
            for direction in range(4):
                new_state, changed = self.move(state, direction)
                if changed:
                    # Use spawn_children to handle probabilistic apple spawning
                    for child_state, prob in self.spawn_children(new_state):
                        # Check if the child state exists in our enumerated states
                        if child_state in state_to_idx:
                            j = state_to_idx[child_state]
                            edges_w.append((i, j, prob))
                        else:
                            # Dynamically add states that weren't enumerated initially
                            states.append(child_state)
                            j = len(states) - 1
                            state_to_idx[child_state] = j
                            # Add labels for the new state
                            labels[j] = {
                                'state': child_state,
                                'score': self.board_score(child_state),
                                'expected_score': self.expected_score(child_state),
                                'display': self.board_to_display(child_state)
                            }
                            edges_w.append((i, j, prob))
            i += 1
        
        return states, edges_w, labels

    def initial_state(self, nodes, edges_w, labels):
        """Return index of initial state - snake length 1 at (0,0), apple at bottom-right."""
        # Place apple at bottom-right corner of the grid
        apple_pos = (self.SHAPE[0] - 1, self.SHAPE[1] - 1)
        initial_state = (((0, 0),), apple_pos)  # snake at top-left, apple at bottom-right
        for i, label in labels.items():
            if label['state'] == initial_state:
                return i
        return 0  # fallback

    def get_restart_desc(self):
        """Return restart button description."""
        return "Restart Snake"

    def flet_display(self, state):
        """Create a Flet display for the Snake game board."""
        
        board = self.state_to_board(state)
        h, w = board.shape
        
        # Create grid container
        board_container = ft.Column(spacing=1, alignment=ft.MainAxisAlignment.CENTER)
        
        for i in range(h):
            row_controls = []
            for j in range(w):
                cell_value = int(board[i, j])
                
                if cell_value == 0:
                    # Empty space
                    cell_container = ft.Container(
                        content=ft.Text("", text_align=ft.TextAlign.CENTER),
                        width=25,
                        height=25,
                        bgcolor=ft.Colors.BLACK,
                        border_radius=2,
                        alignment=ft.alignment.center,
                        border=ft.border.all(1, ft.Colors.GREY_700)
                    )
                elif cell_value == 3:
                    # Food (apple)
                    cell_container = ft.Container(
                        content=ft.Text(
                            "🍎",
                            size=16,
                            text_align=ft.TextAlign.CENTER
                        ),
                        width=25,
                        height=25,
                        bgcolor=ft.Colors.BLACK,
                        border_radius=2,
                        alignment=ft.alignment.center,
                        border=ft.border.all(1, ft.Colors.GREY_700)
                    )
                elif cell_value == 2:
                    # Snake head
                    cell_container = ft.Container(
                        content=ft.Text(
                            "🐍",
                            size=16,
                            text_align=ft.TextAlign.CENTER
                        ),
                        width=25,
                        height=25,
                        bgcolor=ft.Colors.GREEN_400,
                        border_radius=2,
                        alignment=ft.alignment.center,
                        border=ft.border.all(1, ft.Colors.GREEN_600)
                    )
                elif cell_value == 1:
                    # Snake body/tail
                    cell_container = ft.Container(
                        content=ft.Text("", text_align=ft.TextAlign.CENTER),
                        width=25,
                        height=25,
                        bgcolor=ft.Colors.GREEN_600,
                        border_radius=2,
                        alignment=ft.alignment.center,
                        border=ft.border.all(1, ft.Colors.GREEN_700)
                    )
                else:
                    # Unknown value - fallback to empty
                    cell_container = ft.Container(
                        content=ft.Text("", text_align=ft.TextAlign.CENTER),
                        width=25,
                        height=25,
                        bgcolor=ft.Colors.GREY_500,
                        border_radius=2,
                        alignment=ft.alignment.center,
                        border=ft.border.all(1, ft.Colors.GREY_700)
                    )
                
                row_controls.append(cell_container)
            
            board_container.controls.append(
                ft.Row(row_controls, spacing=1, alignment=ft.MainAxisAlignment.CENTER)
            )
        
        return ft.Container(
            content=board_container,
            padding=15,
            bgcolor=ft.Colors.GREY_900,
            border_radius=10,
            alignment=ft.alignment.center
        )

    def create_game_buttons(self, visualizer):
        """Create Snake-specific buttons with proper wrapping layout."""
        
        # Create directional move buttons with nice styling
        move_buttons = []
        button_configs = [
            (0, '⬆️ Up', ft.Colors.LIGHT_BLUE_400),
            (1, '⬇️ Down', ft.Colors.LIGHT_BLUE_400), 
            (2, '⬅️ Left', ft.Colors.LIGHT_BLUE_400),
            (3, '➡️ Right', ft.Colors.LIGHT_BLUE_400)
        ]
        
        for direction, text, bgcolor in button_configs:
            button = GameButton(
                text=text,
                on_click_fn=lambda e, d=direction: visualizer.on_move_button_click(d)(e),
                width=100,
                height=45,
                bgcolor=bgcolor,
                color=ft.Colors.WHITE
            )
            move_buttons.append(button)
        
        # Create control buttons
        restart_button = GameButton(
            text="🐍 New Snake Game",
            on_click_fn=visualizer.on_restart_button_click,
            bgcolor=ft.Colors.GREEN_600,
            color=ft.Colors.WHITE,
            width=180,
            height=45
        )
        
        luck_button = GameButton(
            text="🎲 Luck: OFF",
            on_click_fn=visualizer.on_luck_button_click,
            bgcolor=ft.Colors.ORANGE_400,
            color=ft.Colors.WHITE,
            width=120,
            height=45
        )
        
        return {
            'move': move_buttons,
            'control': [restart_button, luck_button]
        }
