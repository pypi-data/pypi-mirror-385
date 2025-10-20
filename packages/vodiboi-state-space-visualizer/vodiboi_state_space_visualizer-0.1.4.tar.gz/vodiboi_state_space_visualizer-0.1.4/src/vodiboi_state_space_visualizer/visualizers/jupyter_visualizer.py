"""
Jupyter Notebook State Space Visualizer using Plotly and IPython widgets.
"""

import random
import numpy as np
import plotly.graph_objects as go
from plotly.offline import iplot, init_notebook_mode
import plotly.io as pio
import networkx as nx
from IPython.display import display, clear_output
import ipywidgets as widgets
from ipywidgets import Button, ToggleButton, VBox, HBox, Output, HTML
try:
    from plotly.graph_objs import FigureWidget
    FIGURE_WIDGET_AVAILABLE = True
except ImportError:
    FIGURE_WIDGET_AVAILABLE = False

try:
    import scipy.sparse as sp
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from vodiboi_state_space_visualizer.games import Game


class JupyterStateSpaceVisualizer:
    """
    Jupyter Notebook-based State Space Visualizer with Plotly graphs and IPython widgets.
    
    This visualizer provides a simplified interface for exploring game state spaces
    in Jupyter notebooks with random movement and diffusion coloring capabilities.
    
    Example usage:
    ```
    from vodiboi_state_space_visualizer.games import Game2048
    from vodiboi_state_space_visualizer.visualizers import JupyterStateSpaceVisualizer
    
    game = Game2048(shape=(2, 2))
    visualizer = JupyterStateSpaceVisualizer()
    visualizer.visualize(game)
    ```
    """
    
    def __init__(
        self,
        node_size=3,
        edge_width=1,
        edge_opacity=0.1,
        layout_seed=23,
        ignore_leaves=True,
        ALL_STATES=True,
        colorscale='Plasma',
        dimension=3,
        figure_width=800,
        figure_height=600,
        verbose=True
    ):
        """
        Args:
            node_size (int): Size of nodes in the graph visualization.
            edge_width (int): Width of edges in the graph.
            edge_opacity (float): Opacity of edges (0-1).
            layout_seed (int): Random seed for graph layout.
            ignore_leaves (bool): Whether to ignore leaf nodes in graph generation.
            ALL_STATES (bool): Whether to use all states or only reachable states.
            colorscale (str): Plotly colorscale for node coloring.
            dimension (int): Graph dimension (2 or 3).
            figure_width (int): Width of the Plotly figure.
            figure_height (int): Height of the Plotly figure.
            verbose (bool): Whether to print status messages and debug output.
        """
        self.node_size = node_size
        self.edge_width = edge_width
        self.edge_opacity = edge_opacity
        self.layout_seed = layout_seed
        self.ignore_leaves = ignore_leaves
        self.ALL_STATES = ALL_STATES
        self.colorscale = colorscale
        self.dimension = 3 if dimension not in [2, 3] else dimension
        self.figure_width = figure_width
        self.figure_height = figure_height
        self.verbose = verbose
        
        # Game and state tracking
        self.game = None
        self.nodes = []
        self.edges_w = []
        self.labels = {}
        self.xyz = None
        self.selected_idx = 0
        self.current_state = None
        
        # Diffusion coloring state
        self.use_diffusion_coloring = False
        self.diffusion_probabilities = None
        self.diffusion_steps = 50
        
        # UI components
        self.random_button = None
        self.diffusion_button = None
        self.recalculate_button = None
        self.state_display = None
        self.output_area = None
        self.figure_widget = None
        self.graph_initialized = False
        
        # Initialize notebook mode for Plotly
        init_notebook_mode(connected=True)

    def create_layout(self, n, edges_w):
        """Create 2D or 3D layout for nodes using NetworkX."""
        G = nx.Graph()
        G.add_nodes_from(range(n))
        for u, v, w in edges_w:
            G.add_edge(u, v, weight=float(w))
        
        # Set random seed for reproducible layouts
        np.random.seed(self.layout_seed)
        
        if self.dimension == 2:
            # Try planar layout first, fallback to spring layout
            try:
                if nx.is_planar(G):
                    pos = nx.planar_layout(G, scale=2)
                else:
                    pos = nx.spring_layout(G, k=1/np.sqrt(n), iterations=50, seed=self.layout_seed)
            except:
                pos = nx.spring_layout(G, k=1/np.sqrt(n), iterations=50, seed=self.layout_seed)
        else:
            # Use spring layout for 3D
            try:
                pos = nx.spring_layout(G, dim=3, k=1/np.sqrt(n), iterations=50, seed=self.layout_seed)
            except:
                # Fallback to random positions
                pos = {i: np.random.randn(3) for i in range(n)}
        
        # Process positions
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
        
        return xyz

    def create_plotly_figure(self):
        """Create the Plotly graph figure."""
        if not self.nodes:
            return go.Figure()

        n = len(self.nodes)
        self.xyz = self.create_layout(n, self.edges_w)
        
        fig = go.Figure()
        
        # Add edges
        for i, j, weight in self.edges_w:
            if self.dimension == 3:
                fig.add_trace(go.Scatter3d(
                    x=[self.xyz[i, 0], self.xyz[j, 0], None],
                    y=[self.xyz[i, 1], self.xyz[j, 1], None],
                    z=[self.xyz[i, 2], self.xyz[j, 2], None],
                    mode='lines',
                    line=dict(color='rgba(100,100,100,{})'.format(self.edge_opacity), width=self.edge_width),
                    showlegend=False,
                    hoverinfo='none'
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=[self.xyz[i, 0], self.xyz[j, 0], None],
                    y=[self.xyz[i, 1], self.xyz[j, 1], None],
                    mode='lines',
                    line=dict(color='rgba(100,100,100,{})'.format(self.edge_opacity), width=self.edge_width),
                    showlegend=False,
                    hoverinfo='none'
                ))
        
        # Prepare node colors and hover text
        if self.use_diffusion_coloring and self.diffusion_probabilities is not None:
            node_colors = self.diffusion_probabilities.tolist()
            colorscale = 'Hot'
            colorbar_title = "Probability"
            hover_text = [f"Node {i}: {self.game.board_to_display(self.labels[i]['state'])}<br>Probability: {self.diffusion_probabilities[i]:.4f}" 
                         for i in range(n)]
        else:
            node_colors = [self.game.state_scalar(self.labels[i]['state']) for i in range(n)]
            colorscale = self.colorscale
            colorbar_title = self.game.colorbar_title
            hover_text = [f"Node {i}: {self.game.board_to_display(self.labels[i]['state'])}" 
                         for i in range(n)]
        
        # Add nodes with click event support
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
                name='Nodes'
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
                name='Nodes'
            ))
        
        # Add selected node highlight
        if self.selected_idx < n:
            if self.dimension == 3:
                fig.add_trace(go.Scatter3d(
                    x=[self.xyz[self.selected_idx, 0]],
                    y=[self.xyz[self.selected_idx, 1]],
                    z=[self.xyz[self.selected_idx, 2]],
                    mode='markers',
                    marker=dict(size=self.node_size * 2, color='red', symbol='diamond'),
                    showlegend=False,
                    name='Selected'
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=[self.xyz[self.selected_idx, 0]],
                    y=[self.xyz[self.selected_idx, 1]],
                    mode='markers',
                    marker=dict(size=self.node_size * 2, color='red', symbol='diamond'),
                    showlegend=False,
                    name='Selected'
                ))
        
        # Layout configuration with dark theme
        layout_config = dict(
            width=self.figure_width,
            height=self.figure_height,
            paper_bgcolor='#2E2E2E',
            plot_bgcolor='#2E2E2E',
            margin=dict(l=0, r=0, t=30, b=0),
            font=dict(color='white')
        )
        
        if self.dimension == 3:
            layout_config['scene'] = dict(
                bgcolor='#2E2E2E',
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectmode='cube',
                camera=dict(eye=dict(x=1.2, y=1.2, z=0.6))
            )
        else:
            layout_config.update(dict(
                xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
                yaxis=dict(visible=False)
            ))
        
        fig.update_layout(**layout_config)
        return fig

    def compute_diffusion_probabilities(self):
        """Compute probability diffusion over the state space graph."""
        if not SCIPY_AVAILABLE:
            if self.verbose:
                print("Warning: scipy not available, cannot compute diffusion probabilities")
            return None
            
        if not self.nodes or not self.edges_w:
            return None
        
        n = len(self.nodes)
        
        # Build adjacency matrix
        row_indices = []
        col_indices = []
        
        for i, j, weight in self.edges_w:
            row_indices.append(i)
            col_indices.append(j)
            # Add reverse edge for symmetric diffusion
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
                print(f"Step {step}: range [{prob_dist.min():.6f}, {prob_dist.max():.6f}]")
        
        if self.verbose:
            print(f"✅ Diffusion complete")
        return prob_dist

    def on_random_move(self, button):
        """Handle random move button click."""
        if not self.game or self.current_state is None:
            return
        
        # Get neighbors from edges
        neighbors = []
        for i, j, weight in self.edges_w:
            if i == self.selected_idx:
                neighbors.append(j)
            elif j == self.selected_idx:
                neighbors.append(i)
        
        if neighbors:
            # Select random neighbor
            new_idx = random.choice(neighbors)
            self.selected_idx = new_idx
            self.current_state = self.labels[new_idx]['state']
            
            # Efficient update - only change what's needed
            self.update_display()
        else:
            if self.verbose:
                print("No neighbors available for random move")

    def on_diffusion_toggle(self, change):
        """Handle diffusion coloring toggle."""
        if self.verbose:
            print(f"🔄 Diffusion toggle callback triggered: {change['old']} → {change['new']}")
        self.use_diffusion_coloring = change['new']
        
        if self.use_diffusion_coloring:
            if not SCIPY_AVAILABLE:
                if self.verbose:
                    print("❌ Cannot use diffusion coloring: scipy not available")
                self.use_diffusion_coloring = False
                self.diffusion_button.value = False
                return
            
            self.recalculate_button.disabled = False
            if self.diffusion_probabilities is None:
                self.diffusion_probabilities = self.compute_diffusion_probabilities()
                if self.diffusion_probabilities is None:
                    if self.verbose:
                        print("❌ Failed to compute diffusion probabilities")
                    self.use_diffusion_coloring = False
                    self.diffusion_button.value = False
                    return
        else:
            self.recalculate_button.disabled = True
        
        # Update node colors efficiently
        self.update_node_colors()
        
        if self.verbose:
            mode = "Diffusion Probability" if self.use_diffusion_coloring else "Game State"
            print(f"🎨 Switched to {mode} coloring")
            
            if self.use_diffusion_coloring and self.diffusion_probabilities is not None:
                prob_range = f"[{self.diffusion_probabilities.min():.6f}, {self.diffusion_probabilities.max():.6f}]"
                print(f"   Probability range: {prob_range}")

    def on_recalculate_diffusion(self, button):
        """Recalculate diffusion probabilities."""
        if self.verbose:
            print("🔄 Recalculating diffusion probabilities...")
        self.diffusion_probabilities = self.compute_diffusion_probabilities()
        
        if self.use_diffusion_coloring:
            self.update_node_colors()

    def on_click_handler(self, trace, points, state):
        """Handle click events on the graph."""
        if points.point_inds:
            # Get the clicked node index
            clicked_idx = points.point_inds[0]
            if hasattr(points, 'customdata') and len(points.customdata) > 0:
                clicked_idx = points.customdata[0]
            
            # Update selection
            self.selected_idx = clicked_idx
            self.current_state = self.labels[clicked_idx]['state']
            
            # Update only the highlight and state display
            self.update_highlight_only()
            self.update_state_display()

    def update_node_colors(self):
        """Update node colors based on current coloring mode."""
        if self.verbose:
            print(f"🔄 Updating node colors... (diffusion: {self.use_diffusion_coloring})")
        
        if not self.figure_widget or not FIGURE_WIDGET_AVAILABLE:
            if self.verbose:
                print("   Fallback to full redraw (no FigureWidget)")
            # Fallback to full redraw if FigureWidget not available
            self.update_display(force_redraw=True)
            return
        
        # Find the nodes trace (the one with customdata)
        nodes_trace_idx = None
        for i, trace in enumerate(self.figure_widget.data):
            if hasattr(trace, 'customdata') and trace.customdata is not None:
                nodes_trace_idx = i
                break
        
        if nodes_trace_idx is None:
            if self.verbose:
                print("   Fallback to full redraw (nodes trace not found)")
            # Fallback to full redraw if we can't find the nodes trace
            self.update_display(force_redraw=True)
            return
        
        n = len(self.nodes)
        
        # Prepare new colors and hover text
        if self.use_diffusion_coloring and self.diffusion_probabilities is not None:
            node_colors = self.diffusion_probabilities.tolist()
            colorscale = 'Hot'
            colorbar_title = "Probability"
            hover_text = [f"Node {i}: {self.game.board_to_display(self.labels[i]['state'])}<br>Probability: {self.diffusion_probabilities[i]:.4f}" 
                         for i in range(n)]
        else:
            node_colors = [self.game.state_scalar(self.labels[i]['state']) for i in range(n)]
            colorscale = self.colorscale
            colorbar_title = self.game.colorbar_title
            hover_text = [f"Node {i}: {self.game.board_to_display(self.labels[i]['state'])}" 
                         for i in range(n)]
        
        # Update the nodes trace with new colors
        with self.figure_widget.batch_update():
            # Update marker colors and colorscale
            self.figure_widget.data[nodes_trace_idx].marker.color = node_colors
            self.figure_widget.data[nodes_trace_idx].marker.colorscale = colorscale
            
            # Update colorbar title safely
            try:
                if hasattr(self.figure_widget.data[nodes_trace_idx].marker.colorbar, 'title'):
                    if hasattr(self.figure_widget.data[nodes_trace_idx].marker.colorbar.title, 'text'):
                        self.figure_widget.data[nodes_trace_idx].marker.colorbar.title.text = colorbar_title
                    else:
                        self.figure_widget.data[nodes_trace_idx].marker.colorbar.title = colorbar_title
            except:
                # If colorbar update fails, it's not critical
                pass
            
            # Update hover text
            self.figure_widget.data[nodes_trace_idx].text = hover_text
        
        if self.verbose:
            print(f"   ✅ Node colors updated successfully (trace {nodes_trace_idx})")

    def update_display(self, force_redraw=False):
        """Update the visualization and state display."""
        if not self.graph_initialized or force_redraw:
            # Full redraw
            with self.output_area:
                clear_output(wait=True)
                
                # Create figure
                fig = self.create_plotly_figure()
                
                if FIGURE_WIDGET_AVAILABLE:
                    # Use FigureWidget for interactivity
                    self.figure_widget = FigureWidget(fig)
                    # Add click handler to the nodes trace
                    if len(self.figure_widget.data) > 0:
                        # Find the nodes trace (the one with customdata)
                        for trace in self.figure_widget.data:
                            if hasattr(trace, 'customdata') and trace.customdata is not None:
                                trace.on_click(self.on_click_handler)
                                break
                    display(self.figure_widget)
                else:
                    # Fallback to regular iplot
                    iplot(fig, show_link=False)
                
                self.graph_initialized = True
        else:
            # Efficient update - only update highlight
            self.update_highlight_only()
        
        # Always update state display
        self.update_state_display()

    def update_highlight_only(self):
        """Update only the selected node highlight without redrawing the entire graph."""
        if not self.figure_widget or not FIGURE_WIDGET_AVAILABLE:
            # Fallback to full redraw if FigureWidget not available
            self.update_display(force_redraw=True)
            return
        
        # Find the selected node trace (should be the last trace)
        selected_trace_idx = None
        for i, trace in enumerate(self.figure_widget.data):
            if hasattr(trace, 'name') and trace.name == 'Selected':
                selected_trace_idx = i
                break
        
        if selected_trace_idx is not None and self.selected_idx < len(self.xyz):
            # Update existing selected trace
            with self.figure_widget.batch_update():
                if self.dimension == 3:
                    self.figure_widget.data[selected_trace_idx].x = [self.xyz[self.selected_idx, 0]]
                    self.figure_widget.data[selected_trace_idx].y = [self.xyz[self.selected_idx, 1]]
                    self.figure_widget.data[selected_trace_idx].z = [self.xyz[self.selected_idx, 2]]
                else:
                    self.figure_widget.data[selected_trace_idx].x = [self.xyz[self.selected_idx, 0]]
                    self.figure_widget.data[selected_trace_idx].y = [self.xyz[self.selected_idx, 1]]

    def update_state_display(self):
        """Update the state display text."""
        if self.current_state is not None:
            state_text = f"<b>Current State (Node {self.selected_idx}):</b><br>"
            state_text += f"{self.game.board_to_display(self.current_state)}"
            
            if self.use_diffusion_coloring and self.diffusion_probabilities is not None:
                prob = self.diffusion_probabilities[self.selected_idx]
                state_text += f"<br><b>Diffusion Probability:</b> {prob:.6f}"
            
            self.state_display.value = state_text

    def select_node(self, node_idx):
        """Programmatically select a node by index."""
        if 0 <= node_idx < len(self.labels):
            self.selected_idx = node_idx
            self.current_state = self.labels[node_idx]['state']
            self.update_display()
            return True
        else:
            if self.verbose:
                print(f"Invalid node index: {node_idx}. Valid range is 0-{len(self.labels)-1}")
            return False

    def create_controls(self):
        """Create the control widgets."""
        # Random move button
        self.random_button = Button(
            description='🎲 Random Move',
            style={'button_color': 'lightblue'},
            layout={'width': '150px'}
        )
        self.random_button.on_click(self.on_random_move)
        
        # Diffusion toggle button
        self.diffusion_button = ToggleButton(
            value=False,
            description='Diffusion Coloring',
            style={'button_color': 'lightgreen'},
            layout={'width': '150px'}
        )
        self.diffusion_button.observe(self.on_diffusion_toggle, names='value')
        
        # Recalculate button
        self.recalculate_button = Button(
            description='Recalculate',
            disabled=True,
            style={'button_color': 'orange'},
            layout={'width': '120px'}
        )
        self.recalculate_button.on_click(self.on_recalculate_diffusion)
        
        # State display
        self.state_display = HTML(value="")
        
        # Output area for the plot
        self.output_area = Output()
        
        # Control layout
        controls = HBox([
            self.random_button,
            self.diffusion_button,
            self.recalculate_button
        ])
        
        return VBox([
            controls,
            self.state_display,
            self.output_area
        ])

    def visualize(self, game):
        """
        Main method to start the visualization.
        
        Args:
            game: A Game instance to visualize
        """
        self.game = game
        
        # Generate state space
        if self.verbose:
            print(f"Generating state space for {type(game).__name__}...")
        result = game.enumerate_states(ALL_STATES=self.ALL_STATES, ignore_leaves=self.ignore_leaves)
        
        if len(result) == 3:
            self.nodes, self.edges_w, self.labels = result
        else:
            self.nodes, self.edges_w, self.labels, _ = result
        
        if self.verbose:
            print(f"Generated {len(self.nodes)} nodes and {len(self.edges_w)} edges")
        
        # Initialize state
        init_idx = game.initial_state(self.nodes, self.edges_w, self.labels)
        self.selected_idx = init_idx
        self.current_state = self.labels[init_idx]['state']
        
        # Create and display controls
        controls = self.create_controls()
        display(controls)
        
        # Initial display
        self.update_display(force_redraw=True)
        
        if self.verbose:
            print(f"🎮 {type(game).__name__} visualization ready!")
            print("✨ Features:")
            print("  - Click on any node to select it")
            print("  - Use 'Random Move' button to explore randomly")
            print("  - Toggle 'Diffusion Coloring' to see probability distributions")
            print("  - Efficient updates preserve your view when moving between nodes")

