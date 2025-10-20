import random

import networkx as nx
import flet as ft

from .game import Game


class AbstractGraph(Game):
    """
    Abstract Graph game for visualizing arbitrary NetworkX graphs.
    
    This class allows you to explore any graph structure without needing a specific game.
    It provides a random move functionality to traverse the graph randomly.

    Example usage:
    ```
    def main(page: ft.Page):
        G = nx.erdos_renyi_graph(10, 0.3)
        game = AbstractGraph(G)
        visualizer = FletStateSpaceVisualizer(ALL_STATES=True)
        visualizer.build_ui(page, game)
    ft.app(target=main)
    ```
    """
    
    def __init__(self, graph, node_labels=None, edge_weights=None, initial_node=None):
        """
        Initialize the AbstractGraph game.
        
        Args:
            graph (networkx.Graph): The graph to visualize
            node_labels (dict, optional): Mapping from node to display label
            edge_weights (dict, optional): Mapping from edge to weight
            initial_node (any, optional): Starting node (defaults to first node)
        """
        super().__init__()
        
        if not isinstance(graph, nx.Graph):
            raise ValueError("Input must be a NetworkX graph")
        
        if len(graph.nodes()) == 0:
            raise ValueError("Graph must have at least one node")
        
        self.graph = graph.copy()  # Make a copy to avoid modifying original
        self.node_list = list(self.graph.nodes())
        self.edge_list = list(self.graph.edges())
        
        # Set up node labels
        if node_labels is None:
            self.node_labels = {node: str(node) for node in self.node_list}
        else:
            self.node_labels = node_labels.copy()
        
        # Set up edge weights
        if edge_weights is None:
            self.edge_weights = {edge: 1.0 for edge in self.edge_list}
        else:
            self.edge_weights = edge_weights.copy()
        
        # Set initial node
        if initial_node is None:
            self.initial_node = self.node_list[0]
        else:
            if initial_node not in self.graph.nodes():
                raise ValueError(f"Initial node {initial_node} not in graph")
            self.initial_node = initial_node
        
        # Game configuration
        self.button_names = ["🎲 Random Move"]
        self.button_dirs = [0]
        self.colorbar_title = "Node Index"
        self.ignore_leaves = False
        
        # Create node to index mapping for state representation
        self.node_to_idx = {node: i for i, node in enumerate(self.node_list)}
        self.idx_to_node = {i: node for i, node in enumerate(self.node_list)}
    
    def move(self, state, direction):
        """Perform a random move to a neighboring node."""
        current_node_idx = state
        current_node = self.idx_to_node[current_node_idx]
        
        # Get neighbors
        neighbors = list(self.graph.neighbors(current_node))
        
        if not neighbors:
            # No neighbors, stay at current node
            return state, False
        
        # Choose random neighbor
        next_node = random.choice(neighbors)
        next_state = self.node_to_idx[next_node]
        
        return next_state, True
    
    def spawn_children(self, state):
        """AbstractGraph is deterministic - no randomness in state transitions."""
        return [(state, 1.0)]
    
    def board_score(self, state):
        """Score based on node index."""
        return state
    
    def canonical(self, state):
        """Return canonical form of state."""
        return state
    
    def expected_score(self, state):
        """Expected score heuristic."""
        return self.board_score(state)
    
    def state_scalar(self, state):
        """Return node index for coloring."""
        return state
    
    def board_to_display(self, state):
        """Return string representation of the current node."""
        node = self.idx_to_node[state]
        label = self.node_labels.get(node, str(node))
        degree = self.graph.degree(node)
        return f"Node: {label} (degree: {degree})"
    
    def board_annotations(self, board):
        """Return empty annotations for AbstractGraph."""
        return []
    
    def enumerate_states(self, initial_tiles=None, ALL_STATES=True, ignore_leaves=False):
        """Enumerate states based on the graph structure."""
        # States are just node indices
        states = list(range(len(self.node_list)))
        
        # Build edges based on graph connectivity
        edges_w = []
        for u, v in self.graph.edges():
            u_idx = self.node_to_idx[u]
            v_idx = self.node_to_idx[v]
            weight = self.edge_weights.get((u, v), 1.0)
            
            # Add both directions for undirected graphs
            edges_w.append((u_idx, v_idx, weight))
            edges_w.append((v_idx, u_idx, weight))
        
        # Create labels
        labels = {}
        for i, node in enumerate(self.node_list):
            labels[i] = {
                'state': i,
                'node': node,
                'label': self.node_labels.get(node, str(node)),
                'degree': self.graph.degree(node),
                'expected_score': i,
                'neighbors': len(list(self.graph.neighbors(node)))
            }
        
        return states, edges_w, labels
    
    def initial_state(self, nodes, edges_w, labels):
        """Return the index of the initial node."""
        return self.node_to_idx[self.initial_node]
    
    def get_restart_desc(self):
        """Return restart button description."""
        return f"Restart (Node: {self.node_labels.get(self.initial_node, str(self.initial_node))})"
    
    def flet_display(self, state):
        """Create a Flet display for the current node."""
        
        current_node = self.idx_to_node[state]
        node_label = self.node_labels.get(current_node, str(current_node))
        
        # Get node information
        degree = self.graph.degree(current_node)
        neighbors = list(self.graph.neighbors(current_node))
        neighbor_labels = [self.node_labels.get(n, str(n)) for n in neighbors]
        
        # Create info display
        info_column = ft.Column([
            ft.Text(f"Current Node", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Container(
                content=ft.Text(node_label, size=24, weight=ft.FontWeight.BOLD),
                bgcolor=ft.Colors.BLUE_600,
                padding=20,
                border_radius=10,
                alignment=ft.alignment.center
            ),
            
            ft.Text(f"Degree: {degree}", size=14, color=ft.Colors.WHITE70),
            
            ft.Text("Neighbors:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(f"  • {label}  ", size=12, color=ft.Colors.WHITE70)
                        for label in neighbor_labels  # Show all neighbors
                    ] if neighbors else [ft.Text("No neighbors", size=12, color=ft.Colors.GREY_400)],
                    spacing=2,
                    scroll=ft.ScrollMode.AUTO
                ),
                bgcolor=ft.Colors.GREY_800,
                padding=10,
                border_radius=8,
                height=150  # Fixed height

            ),
            
            ft.Divider(color=ft.Colors.GREY_600),
            
            ft.Text("Graph Stats:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text(f"Total Nodes: {len(self.node_list)}", size=12, color=ft.Colors.WHITE70),
            ft.Text(f"Total Edges: {len(self.edge_list)}", size=12, color=ft.Colors.WHITE70),
            
        ], spacing=10)
        
        return ft.Container(
            content=info_column,
            padding=20,
            bgcolor=ft.Colors.GREY_900,
            border_radius=10,
            width=300
        )
