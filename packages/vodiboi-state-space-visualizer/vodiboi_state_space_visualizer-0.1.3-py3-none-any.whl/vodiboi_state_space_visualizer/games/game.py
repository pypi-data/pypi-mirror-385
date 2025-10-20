import flet as ft


class GameButton:
    """
    A standardized button for game controls with consistent size and styling.
    """
    def __init__(self, text, on_click_fn, width=120, height=50, bgcolor=None, color=None):
        self.text = text
        self.on_click_fn = on_click_fn
        self.width = width
        self.height = height
        self.bgcolor = bgcolor
        self.color = color
        self._flet_button = None
    
    def create_flet_button(self):
        """Create and return a Flet button with this button's properties."""
        
        self._flet_button = ft.ElevatedButton(
            text=self.text,
            on_click=self.on_click_fn,
            width=self.width,
            height=self.height,
            bgcolor=self.bgcolor,
            color=self.color
        )
        return self._flet_button
    
    def update_text(self, new_text):
        """Update the button text."""
        self.text = new_text
        if self._flet_button:
            self._flet_button.text = new_text
            self._flet_button.update()
    
    def set_enabled(self, enabled):
        """Enable or disable the button."""
        if self._flet_button:
            self._flet_button.disabled = not enabled
            self._flet_button.update()

class Game:
    """
    Abstract base class for a game.

    Subclasses must implement:
    - move(board, direction): returns (new_board, changed)
    - spawn_children(board): returns list of (child_board, probability)
    - board_score(board): returns a numeric score for the board
    - canonical(board): returns a canonical representation of the board
    - enumerate_states(): returns (nodes, edges, labels) for state space
    - board_to_display(state): returns a string or displayable representation of the board
    - board_annotations(board): returns plotly annotation dicts for the board
    - button_details(): returns list of (name, direction) for move buttons
    - initial_state(nodes, edges_w, labels): returns initial state index for visualization
    - get_restart_desc(): returns restart button description string

    Optional to implement:
    - expected_score(board): returns expected score from this board
    - state_scalar(state): returns a scalar for coloring nodes
    - create_game_buttons(visualizer): returns dict of game buttons
    - flet_display(state): returns a flet.Control object for displaying the board state
    """
    def __init__(self):
        self.button_names = []
        self.button_dirs = []
        self.colorbar_title = "State Value"
        self.colorscale = 'Plasma'
        self.ignore_leaves = True

    def move(self, board, direction):
        """
        Perform a move on the board in the given direction.
        """
        raise NotImplementedError

    def spawn_children(self, board):
        """
        Generate all possible child states from the current board state.
        """
        raise NotImplementedError

    def board_score(self, board):
        """
        Evaluate the board and return a score.
        """
        raise NotImplementedError

    def canonical(self, board):
        """
        Return a canonical representation of the board.
        """
        raise NotImplementedError

    def expected_score(self, board):
        """
        Return the expected score for the given board state.
        """
        raise NotImplementedError

    def enumerate_states(self):
        """
        Enumerate all possible states from the current board state.
        """
        raise NotImplementedError

    def state_scalar(self, state):
        """Return a scalar for coloring nodes."""
        raise NotImplementedError

    def board_to_display(self, state):
        """Return a string or displayable representation of the board."""
        raise NotImplementedError

    def board_annotations(self, board):
        """Return plotly annotation dicts for the board."""
        raise NotImplementedError

    def button_details(self):
        """Return list of (name, direction) for move buttons."""
        return list(zip(self.button_names, self.button_dirs))

    def initial_state(self, nodes, edges_w, labels):
        """Return the index of the initial state for visualization.
        
        Args:
            nodes: List of game states
            edges_w: List of edges with weights
            labels: Dictionary mapping indices to state information
            
        Returns:
            int: Index of the initial state in the nodes list
        """
        raise NotImplementedError

    def get_restart_desc(self):
        """Return the description for the restart button.
        
        Returns:
            str: Description text for the restart button
        """
        raise NotImplementedError
    
    def create_game_buttons(self, visualizer):
        """Create and return a list of GameButton objects for this game.
        
        Args:
            visualizer: The visualizer instance that handles button clicks
            
        Returns:
            dict: Dictionary mapping button types to lists of GameButton objects
                  e.g., {'move': [button1, button2], 'control': [restart_btn, luck_btn]}
        """
        
        # Create move buttons
        move_buttons = []
        for direction, name in zip(self.button_dirs, self.button_names):
            button = GameButton(
                text=name,
                on_click_fn=lambda e, d=direction: visualizer.on_move_button_click(d)(e)
            )
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
    
    def flet_display(self, state):
        """Create a Flet display for the current board state.
        
        Args:
            state: The current game state
        Returns:
            flet.Control: A Flet control object for displaying the board state
        """
        
        board_str = self.board_to_display(state)
        display_control = ft.Text(
            value=str(board_str),
            size=16,
            weight=ft.FontWeight.NORMAL,
            color=ft.Colors.WHITE
        )
        return display_control