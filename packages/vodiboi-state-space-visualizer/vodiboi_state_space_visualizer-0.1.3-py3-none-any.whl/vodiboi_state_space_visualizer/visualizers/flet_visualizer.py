import flet as ft
try:
    import flet_webview as fwv
except:
    # On google colab or something similar most likely
    print("Warning: flet-webview not available, Flet visualizer will not work. Jupyter visualizer will still work.")
    fwv = None
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import networkx as nx

from vodiboi_state_space_visualizer.games import Game, Game2048


class FletStateSpaceVisualizer:
    """
    Flet-based State Space Visualizer with embedded Plotly graph.
    
    Args:
        node_size (int): Size of nodes in the visualization.
        all_edge_width (int): Width of edges.
        all_edge_opacity (float): Opacity of edges.
        layout_seed (int): Random seed for layout generation.
        ignore_leaves (bool): Whether to ignore leaf nodes.
        ALL_STATES (bool): Whether to generate all possible states.
        colorscale (str): Color scale for node coloring.
        dropdown_label (str): Label for the next state dropdown.
        dimension (int): Dimension of the layout (2 or 3).
        verbose (bool): Whether to print status messages and debug output.
    """
    
    def __init__(
        self,
        node_size=4,
        edge_width=1,
        edge_opacity=0.1,
        layout_seed=23,
        ignore_leaves=True,
        ALL_STATES=True,
        colorscale='Plasma',
        dropdown_label="Next State:",
        dimension=3,
        verbose=True
    ):
        self.node_size = node_size
        self.all_edge_width = edge_width
        self.all_edge_opacity = edge_opacity
        self.layout_seed = layout_seed
        self.ignore_leaves = ignore_leaves
        self.ALL_STATES = ALL_STATES
        self.colorscale = colorscale
        self.dropdown_label = dropdown_label
        self.dimension = 3 if dimension not in [2, 3] else dimension  # Validate dimension parameter
        self.verbose = verbose
        
        # State tracking
        self.game = None
        self.nodes = []
        self.edges_w = []
        self.labels = {}
        self.xyz = None
        self.selected_idx = [0]  # Use list to allow modification in nested functions
        self.displayed_board = [None]  # Use list to allow modification in nested functions
        
        # Diffusion coloring state
        self.use_diffusion_coloring = [False]
        self.diffusion_probabilities = None
        self.diffusion_steps = 50
        
        # UI components
        self.webview = None
        self.game_board_display = None
        self.next_states_dropdown = None
        self.status_text = None
        self.restart_button = None
        self.luck_button = None
        self.diffusion_switch = None
        self.recalculate_button = None
        
        # Graph initialization state
        self._graph_initialized = False
        
        # Game state
        self.game = None
        self.nodes = []
        self.edges_w = []
        self.labels = {}
        self.xyz = None
        self.displayed_board = [None]
        self.selected_idx = [0]
        self.luck_mode = [False]
        
        # UI components
        self.webview = None
        self.game_board_display = None
        self.move_buttons = {}
        self.luck_button = None
        self.restart_button = None
        self.next_states_dropdown = None
        self.status_text = None
        self.board_container = None
        
        # Performance optimization state
        self._graph_initialized = False
        self._last_selected_idx = None
        self._last_graph_structure = None

    def layout_3d(self, n, edges_w):
        """Create 2D or 3D layout for nodes using the exact same algorithm as the original visualizer."""
        G = nx.Graph()
        G.add_nodes_from(range(n))
        for u, v, w in edges_w:
            G.add_edge(u, v, weight=float(w))
        
        # Use different layout algorithms based on dimension
        if self.dimension == 2:
            # Try planar layout first, fallback to spring layout if not planar
            try:
                # Check if graph is planar
                # if nx.is_planar(G):
                #     pos = nx.planar_layout(G, scale=1.0)
                # else:
                    # Fallback to spring layout for non-planar graphs
                pos = nx.spring_layout(G, dim=2, weight='weight', seed=self.layout_seed, scale=1.0)
            except Exception:
                # Fallback to spring layout if planar layout fails
                pos = nx.spring_layout(G, dim=2, weight='weight', iterations=300, seed=self.layout_seed)
        else:
            # Use spring layout for 3D
            try:
                pos = nx.spring_layout(G, dim=3, weight='weight', seed=self.layout_seed, scale=1.0)
            except Exception:
                pos = nx.spring_layout(G, dim=3, weight='weight', iterations=300, seed=self.layout_seed)
        
        # Process positions exactly like the original
        xyz = np.array([pos[i] for i in range(n)], dtype=np.float32)
        xyz -= xyz.mean(0, keepdims=True)
        m = float(np.abs(xyz).max())
        if m > 0:
            xyz /= m
        xyz *= 1.5
        
        # For 2D layouts, ensure we have a 3D array by adding a zero z-coordinate
        if self.dimension == 2:
            zeros = np.zeros((xyz.shape[0], 1), dtype=np.float32)
            xyz = np.hstack([xyz, zeros])
        
        return xyz, G

    def create_plotly_figure(self):
        """Create the Plotly 2D or 3D graph figure with original visualizer settings."""
        if not self.nodes:
            # Return dark-themed empty figure
            fig = go.Figure()
            fig.update_layout(
                paper_bgcolor='#2E2E2E',
                plot_bgcolor='#2E2E2E'
            )
            
            if self.dimension == 3:
                fig.update_layout(
                    scene=dict(
                        bgcolor='#2E2E2E',
                        xaxis=dict(visible=False),
                        yaxis=dict(visible=False),
                        zaxis=dict(visible=False)
                    )
                )
            else:
                fig.update_layout(
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False)
                )
            return fig

        n = len(self.nodes)
        
        # Create layout (now returns both xyz and G)
        self.xyz, G = self.layout_3d(n, self.edges_w)
        
        # Create the figure with dark theme
        fig = go.Figure()
        
        # Add all edges with uniform styling
        for i, j, weight in self.edges_w:
            if self.dimension == 3:
                fig.add_trace(go.Scatter3d(
                    x=[self.xyz[i, 0], self.xyz[j, 0]],
                    y=[self.xyz[i, 1], self.xyz[j, 1]],
                    z=[self.xyz[i, 2], self.xyz[j, 2]],
                    mode='lines',
                    line=dict(width=self.all_edge_width, color=f'rgba(128,128,128,{self.all_edge_opacity})'),
                    hoverinfo='none',
                    showlegend=False
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=[self.xyz[i, 0], self.xyz[j, 0]],
                    y=[self.xyz[i, 1], self.xyz[j, 1]],
                    mode='lines',
                    line=dict(width=self.all_edge_width, color=f'rgba(128,128,128,{self.all_edge_opacity})'),
                    hoverinfo='none',
                    showlegend=False
                ))
        
        # Add nodes - handle both regular and diffusion coloring
        if self.use_diffusion_coloring[0] and self.diffusion_probabilities is not None:
            # Use diffusion probabilities for coloring
            node_colors = self.diffusion_probabilities.tolist() if hasattr(self.diffusion_probabilities, 'tolist') else list(self.diffusion_probabilities)
            colorscale = 'Hot'  # Use a heat map style colorscale
            colorbar_title = "Probability"
            hover_text = [f"Node {i}: {self.game.board_to_display(self.labels[i]['state'])}<br>Probability: {self.diffusion_probabilities[i]:.4f}" 
                         for i in range(n)]
        else:
            # Use regular game state coloring
            node_colors = [self.game.state_scalar(self.labels[i]['state']) for i in range(n)]
            colorscale = self.colorscale
            colorbar_title = self.game.colorbar_title
            hover_text = [f"Node {i}: {self.game.board_to_display(self.labels[i]['state'])}" 
                         for i in range(n)]
        
        # Add nodes with appropriate scatter type
        if self.dimension == 3:
            fig.add_trace(go.Scatter3d(
                x=self.xyz[:, 0],
                y=self.xyz[:, 1],
                z=self.xyz[:, 2],
                mode='markers',
                marker=dict(
                    size=self.node_size,
                    color=node_colors,
                    colorscale=colorscale,
                    showscale=True,
                    colorbar=dict(
                        title=dict(text=colorbar_title, font=dict(color='white')),
                        tickfont=dict(color='white')
                    )
                ),
                text=hover_text,
                hovertemplate='%{text}<extra></extra>',
                customdata=list(range(n)),  # Add customdata for click detection
                showlegend=False,
                name='Nodes'  # Add name to help identify this trace
            ))
        else:
            fig.add_trace(go.Scatter(
                x=self.xyz[:, 0],
                y=self.xyz[:, 1],
                mode='markers',
                marker=dict(
                    size=self.node_size,
                    color=node_colors,
                    colorscale=colorscale,
                    showscale=True,
                    colorbar=dict(
                        title=dict(text=colorbar_title, font=dict(color='white')),
                        tickfont=dict(color='white')
                    )
                ),
                text=hover_text,
                hovertemplate='%{text}<extra></extra>',
                customdata=list(range(n)),  # Add customdata for click detection
                showlegend=False,
                name='Nodes'  # Add name to help identify this trace
            ))
        
        # Add selected node highlight (will be managed dynamically for performance)
        if self.selected_idx[0] < n:
            if self.dimension == 3:
                fig.add_trace(go.Scatter3d(
                    x=[self.xyz[self.selected_idx[0], 0]],
                    y=[self.xyz[self.selected_idx[0], 1]],
                    z=[self.xyz[self.selected_idx[0], 2]],
                    mode='markers',
                    marker=dict(size=self.node_size*2, color='red', symbol='diamond'),
                    showlegend=False,
                    name='Selected'
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=[self.xyz[self.selected_idx[0], 0]],
                    y=[self.xyz[self.selected_idx[0], 1]],
                    mode='markers',
                    marker=dict(size=self.node_size*2, color='red', symbol='diamond'),
                    showlegend=False,
                    name='Selected'
                ))
        
        # Layout with dark theme and appropriate axes settings
        layout_config = dict(
            paper_bgcolor='#2E2E2E',
            plot_bgcolor='#2E2E2E',
            margin=dict(l=0, r=0, t=0, b=0),
            height=600,
            font=dict(color='white')
        )
        
        if self.dimension == 3:
            layout_config['scene'] = dict(
                bgcolor='#2E2E2E',
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectmode='cube',
                camera=dict(
                    eye=dict(x=1.2, y=1.2, z=0.6)
                )
            )
        else:
            layout_config.update(dict(
                xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
                yaxis=dict(visible=False)
            ))
        
        fig.update_layout(**layout_config)
        
        return fig

    def update_plotly_graph(self):
        """Update the Plotly graph - full reload only when necessary."""
        if not self.webview:
            return
            
        # Check if we need to initialize the graph for the first time
        if not hasattr(self, '_graph_initialized') or not self._graph_initialized:
            self.initialize_plotly_graph()
        else:
            # Graph already exists, just update the highlight
            self.update_highlight_only()

    def initialize_plotly_graph(self):
        """Initialize the Plotly graph with full HTML load (first time only)."""
        # Generate the figure (now includes customdata automatically)
        fig = self.create_plotly_figure()
        
        click_js = self.get_click_handler_js()
        
        html = pio.to_html(
            fig,
            include_plotlyjs="inline",
            full_html=True,
            post_script=click_js,
            div_id="plotly-div"
        )
        
        self.webview.load_html(html)
        self._graph_initialized = True

    def update_highlight_only(self):
        """Update just the highlight trace without reloading HTML."""
        if not (self.webview and hasattr(self.webview, 'run_javascript')):
            # Fallback to full reload if JavaScript not available
            self._graph_initialized = False
            self.update_plotly_graph()
            return
            
        node_index = self.selected_idx[0]
        
        # JavaScript to update the highlight trace position
        js_code = f"""
        (function() {{
            try {{
                var plotDiv = document.getElementById('plotly-div');
                if (!plotDiv || !plotDiv.data) {{
                    return;
                }}
                
                // Find the nodes trace to get coordinates
                var nodesTrace = null;
                var nodesTraceIndex = -1;
                for (var i = 0; i < plotDiv.data.length; i++) {{
                    if (plotDiv.data[i].name === 'Nodes' || (plotDiv.data[i].customdata && plotDiv.data[i].x && plotDiv.data[i].x.length > {node_index})) {{
                        nodesTrace = plotDiv.data[i];
                        nodesTraceIndex = i;
                        break;
                    }}
                }}
                
                if (!nodesTrace) {{
                    return;
                }}
                
                // Check if coordinates exist in the trace
                var nodeX, nodeY, nodeZ;
                
                if (nodesTrace.x && nodesTrace.x.length > {node_index}) {{
                    nodeX = nodesTrace.x[{node_index}];
                    nodeY = nodesTrace.y[{node_index}];
                    nodeZ = nodesTrace.z ? nodesTrace.z[{node_index}] : undefined;
                }} else if (nodesTrace._fullData && nodesTrace._fullData.x) {{
                    // Try accessing from _fullData (internal Plotly structure)
                    nodeX = nodesTrace._fullData.x[{node_index}];
                    nodeY = nodesTrace._fullData.y[{node_index}];
                    nodeZ = nodesTrace._fullData.z ? nodesTrace._fullData.z[{node_index}] : undefined;
                }} else {{
                    // Try accessing from plotDiv._fullData directly
                    var fullTrace = plotDiv._fullData && plotDiv._fullData[nodesTraceIndex];
                    if (fullTrace && fullTrace.x) {{
                        nodeX = fullTrace.x[{node_index}];
                        nodeY = fullTrace.y[{node_index}];
                        nodeZ = fullTrace.z ? fullTrace.z[{node_index}] : undefined;
                    }}
                }}
                
                if (nodeX === undefined || nodeY === undefined) {{
                    return;
                }}
                
                // Find the selected node trace
                var selectedTraceIndex = -1;
                for (var i = plotDiv.data.length - 1; i >= 0; i--) {{
                    if (plotDiv.data[i].name === 'Selected') {{
                        selectedTraceIndex = i;
                        break;
                    }}
                }}
                
                var is3D = {str(self.dimension == 3).lower()};
                
                if (selectedTraceIndex >= 0) {{
                    // Update existing highlight trace
                    var updateData = {{
                        'x': [[nodeX]],
                        'y': [[nodeY]]
                    }};
                    if (is3D && nodeZ !== undefined) {{
                        updateData['z'] = [[nodeZ]];
                    }}
                    Plotly.restyle('plotly-div', updateData, [selectedTraceIndex]);
                }} else {{
                    // Add new highlight trace
                    var highlightTrace = {{
                        x: [nodeX],
                        y: [nodeY],
                        mode: 'markers',
                        marker: {{
                            size: {self.node_size * 2},
                            color: 'red',
                            symbol: 'diamond'
                        }},
                        showlegend: false,
                        name: 'Selected',
                        type: is3D ? 'scatter3d' : 'scatter'
                    }};
                    
                    if (is3D && nodeZ !== undefined) {{
                        highlightTrace.z = [nodeZ];
                    }}
                    
                    Plotly.addTraces('plotly-div', [highlightTrace]);
                }}
            }} catch(error) {{
                // Silent fallback
            }}
        }})();
        """
        
        try:
            self.webview.run_javascript(js_code)
        except Exception as e:
            # Fallback to full graph update
            self._graph_initialized = False
            self.update_plotly_graph()

    def compute_diffusion_probabilities(self):
        """Compute probability diffusion over the state space graph."""
        try:
            import scipy.sparse as sp
        except ImportError:
            if self.verbose:
                print("Warning: scipy not available, cannot compute diffusion probabilities")
            return None
            
        if not self.nodes or not self.edges_w:
            return None
        
        n = len(self.nodes)
        
        # Build adjacency matrix from game transitions
        row_indices = []
        col_indices = []
        
        for i, j, weight in self.edges_w:
            row_indices.append(i)
            col_indices.append(j)
            # For symmetric diffusion, add reverse edge
            row_indices.append(j)
            col_indices.append(i)
        
        # Create sparse adjacency matrix
        adjacency = sp.csr_matrix(
            (np.ones(len(row_indices)), (row_indices, col_indices)), 
            shape=(n, n)
        )
        
        # Normalize rows to create transition matrix
        row_sums = np.array(adjacency.sum(axis=1)).flatten()
        row_sums[row_sums == 0] = 1  # Avoid division by zero
        
        inv_row_sums = sp.diags(1.0 / row_sums)
        transition_matrix = inv_row_sums @ adjacency
        
        # Initial uniform probability distribution
        prob_dist = np.ones(n) / n
        
        if self.verbose:
            print(f"Computing diffusion over {n} nodes for {self.diffusion_steps} steps...")
        
        # Run diffusion simulation
        for step in range(self.diffusion_steps):
            new_prob_dist = transition_matrix.T @ prob_dist
            prob_dist = new_prob_dist
            
            if step % 25 == 0 and self.verbose:
                print(f"  Step {step}/{self.diffusion_steps} - range: [{prob_dist.min():.6f}, {prob_dist.max():.6f}]")
        
        if self.verbose:
            print(f"✅ Diffusion complete - final range: [{prob_dist.min():.6f}, {prob_dist.max():.6f}]")
        return prob_dist

    def on_diffusion_toggle(self, e):
        """Handle diffusion coloring toggle."""
        self.use_diffusion_coloring[0] = e.control.value
        
        if self.use_diffusion_coloring[0]:
            # Enable recalculate button
            if hasattr(self, 'recalculate_button') and self.recalculate_button:
                self.recalculate_button.disabled = False
                self.recalculate_button.update()
            
            # Compute diffusion probabilities if not already computed
            if self.diffusion_probabilities is None:
                if self.verbose:
                    print("🔄 Computing diffusion probabilities...")
                self.diffusion_probabilities = self.compute_diffusion_probabilities()
        else:
            # Disable recalculate button
            if hasattr(self, 'recalculate_button') and self.recalculate_button:
                self.recalculate_button.disabled = True
                self.recalculate_button.update()
        
        # Force full graph re-render with new coloring
        self._graph_initialized = False
        self.update_plotly_graph()
        
        if self.verbose:
            mode = "Diffusion Probability" if self.use_diffusion_coloring[0] else "Game State"
            print(f"🎨 Switched to {mode} coloring")

    def on_recalculate_diffusion(self, e):
        """Recalculate diffusion probabilities."""
        if self.verbose:
            print("🔄 Recalculating diffusion probabilities...")
        self.diffusion_probabilities = self.compute_diffusion_probabilities()
        
        if self.use_diffusion_coloring[0]:
            self._graph_initialized = False
            self.update_plotly_graph()

    def update_game_board_display(self):
        """Update the game board display."""
        if self.game and self.displayed_board[0] is not None:
            # Use the game's flet_display method if available
            if hasattr(self.game, 'flet_display'):
                new_display = self.game.flet_display(self.displayed_board[0])
                if hasattr(self.game_board_display, 'content'):
                    # It's a Container, update its content
                    self.game_board_display.content = new_display.content
                    self.game_board_display.update()
                else:
                    # It's a TextField, replace with the new display
                    # This shouldn't happen with the new design, but just in case
                    display_text = self.game.board_to_display(self.displayed_board[0])
                    self.game_board_display.value = display_text
                    self.game_board_display.update()
            else:
                # Fallback to text display for games without flet_display
                if hasattr(self.game_board_display, 'value'):
                    display_text = self.game.board_to_display(self.displayed_board[0])
                    self.game_board_display.value = display_text
                    self.game_board_display.update()

    def update_next_states_dropdown(self):
        """Update the next states dropdown options."""
        if not self.game or self.displayed_board[0] is None:
            return
            
        # Get possible next states
        options = [ft.dropdown.Option(key=str(None), text="none")]
        
        current_state = self.displayed_board[0]
        for direction in self.game.button_dirs:
            if isinstance(self.game, Game2048):
                moved, changed = self.game.move_and_spawn(current_state, direction)
            else:
                moved, changed = self.game.move(current_state, direction)
            
            if changed:
                canonical_moved = self.game.canonical(moved)
                state_to_idx = {self.labels[j]['state']: j for j in range(len(self.labels))}
                if canonical_moved in state_to_idx:
                    idx = state_to_idx[canonical_moved]
                    button_name = self.game.button_names[self.game.button_dirs.index(direction)]
                    options.append(ft.dropdown.Option(
                        key=str(idx),
                        text=f"{button_name}: {self.game.board_to_display(moved)[:50]}..."
                    ))
        
        self.next_states_dropdown.options = options
        self.next_states_dropdown.update()

    def _create_wrapped_move_buttons(self):
        """Create a wrapped layout for move buttons that adapts to available space."""
        import flet as ft
        
        # Get flet buttons from GameButton objects
        flet_buttons = []
        for direction in self.game.button_dirs:
            game_button = self.move_buttons[direction]
            flet_buttons.append(game_button._flet_button)
        
        # For 4 buttons, create a 2x2 grid for better wrapping
        if len(flet_buttons) == 4:
            return ft.Column([
                ft.Row([flet_buttons[0], flet_buttons[2]], 
                       alignment=ft.MainAxisAlignment.CENTER, spacing=10),  # Up, Left
                ft.Row([flet_buttons[1], flet_buttons[3]], 
                       alignment=ft.MainAxisAlignment.CENTER, spacing=10),  # Down, Right
            ], spacing=10)
        else:
            # For other numbers, use a wrapping row
            return ft.Row(
                flet_buttons,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                wrap=True
            )

    def update_move_buttons(self):
        """Update move button enabled/disabled state."""
        if not self.game or self.displayed_board[0] is None:
            return
            
        current_state = self.displayed_board[0]
        
        # Handle Klotski with special button state updates
        if hasattr(self.game, 'update_button_states'):
            # Get move buttons as a list in the same order as button_dirs
            move_button_list = []
            for direction in self.game.button_dirs:
                if direction in self.move_buttons:
                    move_button_list.append(self.move_buttons[direction])
            
            # Update Klotski button states with color changes
            self.game.update_button_states(current_state, move_button_list)
        else:
            # Standard button update for other games
            for direction, game_button in self.move_buttons.items():
                moved, changed = self.game.move(current_state, direction)
                game_button.set_enabled(changed)

    def on_move_button_click(self, direction):
        """Handle move button click."""
        def handler(e):
            if not self.game or self.displayed_board[0] is None:
                return
                
            current_state = self.displayed_board[0]
            
            if isinstance(self.game, Game2048):
                # Handle Game2048 with luck mode support
                moved_board, changed = self.game.move(current_state, direction)
                if not changed:
                    return
                
                # Get possible children (spawn options)
                children = self.game.spawn_children(moved_board)
                if not children:
                    moved = moved_board
                else:
                    # Choose spawn based on luck mode
                    if self.luck_mode[0]:
                        # Luck mode: choose the child with highest expected score
                        state_to_idx = {self.labels[j]['state']: j for j in range(len(self.labels))}
                        best_child = None
                        best_score = -float('inf')
                        for child_board, prob in children:
                            canonical_child = self.game.canonical(child_board)
                            if canonical_child in state_to_idx:
                                child_idx = state_to_idx[canonical_child]
                                expected_score = self.labels[child_idx].get('expected_score', 
                                                                         self.game.expected_score(canonical_child))
                            else:
                                expected_score = self.game.expected_score(canonical_child)
                            if expected_score > best_score:
                                best_score = expected_score
                                best_child = child_board
                        moved = best_child if best_child is not None else children[0][0]
                    else:
                        # Normal mode: random selection based on probabilities
                        import random
                        total_prob = sum(prob for _, prob in children)
                        rand = random.random() * total_prob
                        cumulative = 0
                        moved = children[-1][0]  # fallback
                        for child_board, prob in children:
                            cumulative += prob
                            if rand <= cumulative:
                                moved = child_board
                                break
            else:
                # Other games (including Snake)
                moved_state, changed = self.game.move(current_state, direction)
                if not changed:
                    return
                
                # Handle probabilistic spawning for games like Snake
                children = self.game.spawn_children(moved_state)
                if not children:
                    moved = moved_state
                else:
                    # Choose spawn based on luck mode
                    if self.luck_mode[0]:
                        # Luck mode: choose the child with highest expected score
                        state_to_idx = {self.labels[j]['state']: j for j in range(len(self.labels))}
                        best_child = None
                        best_score = -float('inf')
                        for child_state, prob in children:
                            canonical_child = self.game.canonical(child_state)
                            if canonical_child in state_to_idx:
                                child_idx = state_to_idx[canonical_child]
                                expected_score = self.labels[child_idx].get('expected_score', 
                                                                         self.game.expected_score(canonical_child))
                            else:
                                expected_score = self.game.expected_score(canonical_child)
                            if expected_score > best_score:
                                best_score = expected_score
                                best_child = child_state
                        moved = best_child if best_child is not None else children[0][0]
                    else:
                        # Normal mode: random selection based on probabilities
                        import random
                        total_prob = sum(prob for _, prob in children)
                        rand = random.random() * total_prob
                        cumulative = 0
                        moved = children[-1][0]  # fallback
                        for child_state, prob in children:
                            cumulative += prob
                            if rand <= cumulative:
                                moved = child_state
                                break
            
            # Update state
            self.displayed_board[0] = moved
            
            # Find canonical node for graph selection
            canonical_moved = self.game.canonical(moved)
            state_to_idx = {self.labels[j]['state']: j for j in range(len(self.labels))}
            if canonical_moved in state_to_idx:
                self.selected_idx[0] = state_to_idx[canonical_moved]
            
            # Update UI
            self.update_game_board_display()
            self.update_move_buttons()
            self.update_next_states_dropdown()
            self.update_plotly_graph()
            
            # Update status
            self.status_text.value = f"Board (after {self.game.button_names[self.game.button_dirs.index(direction)]}): {self.game.board_to_display(moved)}"
            self.status_text.update()
        
        return handler

    def on_luck_button_click(self, e):
        """Toggle luck mode."""
        self.luck_mode[0] = not self.luck_mode[0]
        luck_text = f"🎲 Luck: {'ON' if self.luck_mode[0] else 'OFF'}"
        if hasattr(self.luck_button, 'update_text'):
            self.luck_button.update_text(luck_text)
        else:
            # Fallback for old button system
            self.luck_button.text = luck_text
            self.luck_button.update()

    def on_restart_button_click(self, e):
        """Restart to initial state."""
        if self.game and self.labels:
            init_idx = self.game.initial_state(self.nodes, self.edges_w, self.labels)
            self.selected_idx[0] = init_idx
            self.displayed_board[0] = self.labels[init_idx]['state']
            
            self.update_game_board_display()
            self.update_move_buttons()
            self.update_next_states_dropdown()
            self.update_plotly_graph()
            
            self.status_text.value = f"Restarted to initial state"
            self.status_text.update()

    def on_dropdown_change(self, e):
        """Handle next state dropdown selection."""
        if e.control.value and e.control.value != "None":
            try:
                idx = int(e.control.value)
                self.select_node(idx)
            except (ValueError, KeyError):
                pass

    def select_node(self, idx, update_graph=True):
        """Select a node by index and update all displays."""
        if 0 <= idx < len(self.labels):
            self.selected_idx[0] = idx
            self.displayed_board[0] = self.labels[idx]['state']
            
            self.update_game_board_display()
            self.update_move_buttons()
            self.update_next_states_dropdown()
            self.update_plotly_graph()
            
            self.status_text.value = f"Selected state {idx}: {self.game.board_to_display(self.labels[idx]['state'])}"
            self.status_text.update()

    def on_webview_loaded(self, e):
        """Handle webview page loaded."""
        pass

    def on_console_message(self, e):
        """Handle console messages from the webview (for click detection)."""
        import json
        
        msg = e.message or ""
        if self.verbose:
            print(f"Console: {msg}")  # Debug output
        
        if msg.startswith("PLOTLY_NODE_CLICK:"):
            try:
                data = json.loads(msg.split(":", 1)[1])
                node_index = data.get("nodeIndex")
                if node_index is not None:
                    # Select the clicked node
                    self.select_node(node_index)
            except (json.JSONDecodeError, KeyError, ValueError) as ex:
                if self.verbose:
                    print(f"Error parsing click data: {ex}")



    def get_click_handler_js(self):
        """Generate the JavaScript for handling clicks."""
        return f"""
        (function() {{
            var plotDiv = document.getElementById('plotly-div');
            if (!plotDiv) {{
                return;
            }}
            
            plotDiv.on('plotly_click', function(evt) {{
                var pt = evt.points && evt.points[0];
                if (!pt) return;
                
                // Only handle clicks on nodes trace (the one with customdata)
                if (pt.data && pt.data.customdata && pt.customdata !== undefined) {{
                    var payload = {{
                        curveNumber: pt.curveNumber,
                        pointNumber: pt.pointNumber,
                        nodeIndex: pt.customdata
                    }};
                    console.log("PLOTLY_NODE_CLICK:" + JSON.stringify(payload));
                }}
            }});
        }})();
        """

    def update_highlight_fast(self):
        """Fast highlight update using Plotly.restyle - avoids full HTML regeneration."""
        if not (self.webview and hasattr(self.webview, 'run_javascript')):
            # Fallback to full update if JavaScript execution not available
            self._graph_initialized = False
            self.update_plotly_graph()
            return
            
        node_index = self.selected_idx[0]
        
        # JavaScript to update just the highlight trace position
        js_code = f"""
        (function() {{
            var plotDiv = document.getElementById('plotly-div');
            if (!plotDiv || !plotDiv.data) return;
            
            // Find the nodes trace to get coordinates
            var nodesTrace = null;
            for (var i = 0; i < plotDiv.data.length; i++) {{
                if (plotDiv.data[i].customdata && plotDiv.data[i].x && plotDiv.data[i].x.length > {node_index}) {{
                    nodesTrace = plotDiv.data[i];
                    break;
                }}
            }}
            
            if (!nodesTrace) return;
            
            var nodeX = nodesTrace.x[{node_index}];
            var nodeY = nodesTrace.y[{node_index}];
            var nodeZ = nodesTrace.z ? nodesTrace.z[{node_index}] : undefined;
            
            // Find and update the selected node trace
            var selectedTraceIndex = -1;
            for (var i = plotDiv.data.length - 1; i >= 0; i--) {{
                if (plotDiv.data[i].name === 'Selected') {{
                    selectedTraceIndex = i;
                    break;
                }}
            }}
            
            var is3D = {str(self.dimension == 3).lower()};
            
            if (selectedTraceIndex >= 0) {{
                // Update existing highlight trace position
                var updateData = {{
                    'x': [[nodeX]],
                    'y': [[nodeY]]
                }};
                if (is3D && nodeZ !== undefined) {{
                    updateData['z'] = [[nodeZ]];
                }}
                Plotly.restyle('plotly-div', updateData, [selectedTraceIndex]);
            }} else {{
                // Add new highlight trace if it doesn't exist
                var highlightTrace = {{
                    x: [nodeX],
                    y: [nodeY],
                    mode: 'markers',
                    marker: {{
                        size: {self.node_size * 2},
                        color: 'red',
                        symbol: 'diamond'
                    }},
                    showlegend: false,
                    name: 'Selected',
                    type: is3D ? 'scatter3d' : 'scatter'
                }};
                
                if (is3D && nodeZ !== undefined) {{
                    highlightTrace.z = [nodeZ];
                }}
                
                Plotly.addTraces('plotly-div', [highlightTrace]);
            }}
            
            console.log("PLOTLY_DEBUG: fast highlight update to node {node_index}");
        }})();
        """
        
        try:
            self.webview.run_javascript(js_code)
        except Exception as e:
            if self.verbose:
                print(f"Error in fast highlight update: {e}")
            # Fallback to full update
            self._graph_initialized = False
            self.update_plotly_graph()

    def highlight_selected_node_in_graph(self, node_index):
        """Simple approach: just update the graph."""
        self.update_plotly_graph()

    





    def build_ui(self, page: ft.Page, game: Game):
        """Build the Flet UI for the given game."""
        self.game = game
        self.page = page  # Store page reference for updates
        
        # Generate state space
        result = game.enumerate_states(ALL_STATES=self.ALL_STATES, ignore_leaves=self.ignore_leaves)
        if len(result) == 3:
            self.nodes, self.edges_w, self.labels = result
        else:
            self.nodes, self.edges_w, self.labels, _ = result
        
        # Initialize state
        init_idx = game.initial_state(self.nodes, self.edges_w, self.labels)
        self.selected_idx[0] = init_idx
        self.displayed_board[0] = self.labels[init_idx]['state']
        
        # Page configuration
        page.title = f"State Space Visualizer - {type(game).__name__}"
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = ft.Colors.GREY_900
        page.window_min_width = 1200
        page.window_min_height = 800
        
        # Create webview for Plotly graph with console message handling
        self.webview = fwv.WebView(
            url="about:blank",
            expand=True,
            width=600,
            height=600,
            enable_javascript=True,
            on_console_message=self.on_console_message
        )
        
        # Create game board display - now uses flet_display method from game class
        if hasattr(game, 'flet_display'):
            # Use the game's flet_display method
            initial_display = game.flet_display(self.displayed_board[0])
            self.game_board_display = ft.Container(
                content=initial_display.content,
                padding=initial_display.padding,
                bgcolor=initial_display.bgcolor,
                border_radius=initial_display.border_radius,
                alignment=initial_display.alignment,
                width=initial_display.width,
                height=initial_display.height
            )
        else:
            # Fallback to text display for games without flet_display
            self.game_board_display = ft.TextField(
                value="",
                multiline=True,
                read_only=True,
                width=300,
                height=200,
                text_size=12,
                bgcolor=ft.Colors.GREY_700,
                color=ft.Colors.WHITE,
                border_color=ft.Colors.GREY_600
            )
        
        # Create game buttons using the game's own button creation method
        game_buttons = game.create_game_buttons(self)
        
        # Store move buttons for later reference (maintaining old interface)
        self.move_buttons = {}
        for i, button in enumerate(game_buttons['move']):
            direction = game.button_dirs[i]
            flet_button = button.create_flet_button()
            self.move_buttons[direction] = button  # Store GameButton object
            button._flet_button = flet_button  # Keep reference to flet button
        
        # Store control buttons
        control_buttons = game_buttons['control']
        self.restart_button = control_buttons[0]  # First control button is restart
        self.luck_button = control_buttons[1] if len(control_buttons) > 1 else None
        
        # Create flet buttons for controls
        restart_flet = self.restart_button.create_flet_button()
        luck_flet = self.luck_button.create_flet_button() if self.luck_button else None
        
        # Create next states dropdown
        self.next_states_dropdown = ft.Dropdown(
            label=self.dropdown_label,
            options=[],
            on_change=self.on_dropdown_change,
            width=400
        )
        
        # Create status text
        self.status_text = ft.Text(
            value=f"Initial state: {game.board_to_display(self.displayed_board[0])}",
            size=12,
            color=ft.Colors.GREY_300
        )
        
        # Create diffusion controls
        self.diffusion_switch = ft.Switch(
            label="Diffusion Coloring",
            value=False,
            on_change=self.on_diffusion_toggle
        )
        
        self.recalculate_button = ft.ElevatedButton(
            "Recalculate",
            on_click=self.on_recalculate_diffusion,
            disabled=True
        )
        
        
        # Layout with dark theme colors
        controls_column = ft.Column([
            ft.Text(f"{type(game).__name__} Game", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Divider(color=ft.Colors.GREY_600),
            
            ft.Text("Game Board:", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            self.game_board_display,

            ft.Text("Controls:", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Row([
                restart_flet,
                luck_flet
            ] if luck_flet else [restart_flet], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            
            ft.Text("Move:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            self._create_wrapped_move_buttons(),
            
            ft.Text("Navigation:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            self.next_states_dropdown,
            
            ft.Divider(color=ft.Colors.GREY_600),
            ft.Text("Visualization:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Row([
                self.diffusion_switch,
                self.recalculate_button
            ], spacing=10),
            
            ft.Divider(color=ft.Colors.GREY_600),
            ft.Text("Status:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            self.status_text
            
        ], spacing=10, scroll=ft.ScrollMode.AUTO, width=450)
        
        # Main layout with dark theme
        main_row = ft.Row([
            ft.Container(
                content=controls_column,
                padding=20,
                bgcolor=ft.Colors.GREY_800,
                border_radius=10,
                width=470,
                border=ft.border.all(1, ft.Colors.GREY_600)
            ),
            ft.Container(
                content=self.webview,
                padding=20,
                bgcolor=ft.Colors.GREY_900,
                border_radius=10,
                expand=True,
                border=ft.border.all(1, ft.Colors.GREY_600)
            )
        ], spacing=20, expand=True)
        
        page.add(main_row)
        
        # Initialize displays
        self.update_game_board_display()
        self.update_move_buttons()
        self.update_next_states_dropdown()
        self.update_plotly_graph()