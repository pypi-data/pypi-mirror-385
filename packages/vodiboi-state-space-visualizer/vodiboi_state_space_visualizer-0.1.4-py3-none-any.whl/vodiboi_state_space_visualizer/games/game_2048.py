from collections import defaultdict
from functools import lru_cache
import random

import numpy as np
import flet as ft

from .game import Game, GameButton


class Game2048(Game):
    """
    2048 game implementation for state space visualization.
    
    This game represents the popular 2048 sliding tile puzzle where players
    combine tiles with the same numbers to create larger numbers. The state space
    shows all possible board configurations and transitions between them.

    Example usage:
    ```
    def main(page: ft.Page):
        game = Game2048(shape=(2, 2))
        visualizer = FletStateSpaceVisualizer()
        visualizer.build_ui(page, game)
    ft.app(target=main)
    ```
        
    """
    def __init__(self, shape=(1, 4), save_space=True):
        """
        Args:
            shape (tuple): Grid dimensions as (rows, columns). Default is (1, 4).
            save_space (bool): Whether to use memory-efficient state representation.
        """
        super().__init__()
        self.SHAPE = shape
        self.button_names = ['Left', 'Right', 'Up', 'Down']
        self.button_dirs = [0, 1, 2, 3]
        self.colorbar_title = "Max tile (exp)"
        self.save_space = save_space

    def move(self, board, direction):
        n, m = self.SHAPE
        b = [list(board[i*m:(i+1)*m]) for i in range(n)]
        changed = False
        if direction in (0, 1):  # left/right
            new_rows = []
            for row in b:
                r = row[::-1] if direction == 1 else row[:]
                vals = [x for x in r if x != 0]
                merged, i = [], 0
                while i < len(vals):
                    if i + 1 < len(vals) and vals[i] == vals[i + 1]:
                        merged.append(vals[i] + 1)
                        i += 2
                        changed = True
                    else:
                        merged.append(vals[i])
                        i += 1
                merged += [0] * (m - len(merged))
                if direction == 1:
                    merged = merged[::-1]
                if merged != row:
                    changed = True
                new_rows.append(merged)
            new_b = new_rows
        else:  # up/down
            cols = [[b[i][j] for i in range(n)] for j in range(m)]
            new_cols = []
            for col in cols:
                c = col[::-1] if direction == 3 else col[:]
                vals = [x for x in c if x != 0]
                merged, i = [], 0
                while i < len(vals):
                    if i + 1 < len(vals) and vals[i] == vals[i + 1]:
                        merged.append(vals[i] + 1)
                        i += 2
                        changed = True
                    else:
                        merged.append(vals[i])
                        i += 1
                merged += [0] * (n - len(merged))
                if direction == 3:
                    merged = merged[::-1]
                new_cols.append(merged)
            new_b = [[new_cols[j][i] for j in range(m)] for i in range(n)]
            if new_b != b:
                changed = True
        return tuple(x for row in new_b for x in row), changed

    def move_and_spawn(self, board, direction):
        """Complete 2048 move: slide/merge tiles, then spawn a new random tile"""
        
        # First, do the slide and merge
        moved_board, changed = self.move(board, direction)
        
        if not changed:
            # If no tiles moved, return original board
            return board, False
            
        # Get possible children (all ways to spawn new tiles)
        children = self.spawn_children(moved_board)
        
        if not children:
            # No empty spaces to spawn, return the moved board
            return moved_board, True
            
        # Choose one child randomly based on probabilities
        total_prob = sum(prob for _, prob in children)
        rand = random.random() * total_prob
        cumulative = 0
        
        for child_board, prob in children:
            cumulative += prob
            if rand <= cumulative:
                return child_board, True
                
        # Fallback to last child (shouldn't happen with proper probabilities)
        return children[-1][0], True

    def spawn_children(self, board, spawn_probs=[(1, 0.9), (2, 0.1)]):
        empties = [i for i, x in enumerate(board) if x == 0]
        n = len(empties)
        if n == 0:
            return []
        children = []
        for pos in empties:
            for exp, p in spawn_probs:
                nb = list(board)
                nb[pos] = exp
                children.append((tuple(nb), p / n))
        return children

    def board_score(self, board):
        return sum((x - 1) * (1 << x) if x > 0 else 0 for x in board)

    def get_transforms(self):
        n, m = self.SHAPE
        def idx(i, j):
            return i * m + j
        perms = []
        perms.append(tuple(idx(i, j) for i in range(n) for j in range(m)))
        perms.append(tuple(idx(n - 1 - i, m - 1 - j) for i in range(n) for j in range(m)))
        perms.append(tuple(idx(i, m - 1 - j) for i in range(n) for j in range(m)))
        perms.append(tuple(idx(n - 1 - i, j) for i in range(n) for j in range(m)))
        if n == m:
            perms.append(tuple(idx(j, n - 1 - i) for i in range(n) for j in range(m)))
            perms.append(tuple(idx(m - 1 - j, i) for i in range(n) for j in range(m)))
            perms.append(tuple(idx(j, i) for i in range(n) for j in range(m)))
            perms.append(tuple(idx(n - 1 - j, m - 1 - i) for i in range(n) for j in range(m)))
        return perms

    def apply_perm(self, board, perm):
        return tuple(board[i] for i in perm)

    def canonical(self, board):
        if not self.save_space:
            return board
        transforms = self.get_transforms()
        return min(self.apply_perm(board, p) for p in transforms)

    @lru_cache(None)
    def expected_score(self, board):
        if all(not self.move(board, d)[1] for d in range(4)):
            return self.board_score(board)
        best = -1e18
        for d in range(4):
            moved, changed = self.move(board, d)
            if not changed:
                continue
            total = 0.0
            for child, prob in self.spawn_children(moved):
                total += prob * self.expected_score(self.canonical(child))
            best = max(best, total)
        return best

    def enumerate_states(self, initial_tiles=(1, 2), ALL_STATES=False, ignore_leaves=True):
        n, m = self.SHAPE
        size = n * m
        init_raw = set()
        for i in range(size):
            for j in range(i + 1, size):
                for vi in initial_tiles:
                    for vj in initial_tiles:
                        s = [0] * size
                        s[i] = vi
                        s[j] = vj
                        init_raw.add(tuple(s))
        init = {self.canonical(s) for s in init_raw}

        visited, q = set(init), list(init)
        edges = defaultdict(float)
        max_exp = 0
        while q:
            s = q.pop()
            arr = np.array(s, dtype=np.int32)
            max_exp = max(max_exp, int(arr.max(initial=0)))
            for d in range(4):
                moved, changed = self.move(s, d)
                if not changed:
                    continue
                moved_can = self.canonical(moved)
                for child, prob in self.spawn_children(moved_can):
                    v = self.canonical(child)
                    if s != v:
                        edges[(s, v)] = 1
                    if v not in visited:
                        visited.add(v)
                        q.append(v)

        all_states = set(visited)
        if ALL_STATES:
            for vals in np.ndindex(*(max_exp + 1 for _ in range(size))):
                all_states.add(self.canonical(vals))

        for s in all_states:
            for d in range(4):
                moved, changed = self.move(s, d)
                if not changed:
                    continue
                moved_can = self.canonical(moved)
                for child, prob in self.spawn_children(moved_can):
                    v = self.canonical(child)
                    if s != v:
                        edges[(s, v)] = 1

        nodes = list(all_states)
        idx = {s: i for i, s in enumerate(nodes)}
        edges_w = [(idx[u], idx[v], w) for (u, v), w in edges.items() if u in idx and v in idx]

        if ignore_leaves:
            degree = defaultdict(int)
            for u, v, w in edges_w:
                degree[u] += 1
                degree[v] += 1
            keep_nodes = [i for i in range(len(nodes)) if degree[i] > 1]
            old_to_new = {old_idx: new_idx for new_idx, old_idx in enumerate(keep_nodes)}
            nodes = [nodes[i] for i in keep_nodes]
            edges_w = [(old_to_new[u], old_to_new[v], w) for (u, v, w) in edges_w if u in old_to_new and v in old_to_new]

        labels = {}
        for i, s in enumerate(nodes):
            arr = np.array(s, dtype=np.int32)
            labels[i] = {
                'state': s,
                'max_tile': int(arr.max(initial=0)),
                'nnz': int((arr > 0).sum()),
                'sum_exp': int(arr.sum()),
                'expected_score': self.expected_score(s),
            }
        return nodes, edges_w, labels

    def state_scalar(self, state):
        arr = np.array(state, dtype=np.int32)
        return int(arr.max(initial=0))

    def board_to_display(self, state):
        arr = np.array(state).reshape(self.SHAPE)
        board = [[int(2**int(x)) if int(x) > 0 else 0 for x in row] for row in arr]
        return str(board)

    def board_annotations(self, board):
        anns = []
        n, m = board.shape
        for i in range(n):
            for j in range(m):
                val = int(board[i, j])
                text = str(2**val) if val > 0 else '0'
                anns.append(dict(x=j, y=n-1-i, text=text, xanchor='center', yanchor='middle', showarrow=False, font=dict(color='green', size=32)))
        return anns*2

    def initial_state(self, nodes, edges_w, labels):
        """For 2048, find node with minimum state_scalar (lowest max tile)."""
        return min((i for i in labels if self.state_scalar(labels[i]['state']) == min(self.state_scalar(l['state']) for l in labels.values())), default=0)

    def get_restart_desc(self):
        """Return restart button description for 2048."""
        return "Restart (Blue Node)"

    def flet_display(self, state):
        """Create a Flet display for the 2048 game board."""
        
        def get_tile_color(value):
            """Get color for 2048 tile based on value."""
            color_map = {
                0: ft.Colors.GREY_200,
                2: ft.Colors.GREY_100,
                4: ft.Colors.ORANGE_100,
                8: ft.Colors.ORANGE_300,
                16: ft.Colors.ORANGE_500,
                32: ft.Colors.RED_300,
                64: ft.Colors.RED_500,
                128: ft.Colors.YELLOW_300,
                256: ft.Colors.YELLOW_500,
                512: ft.Colors.YELLOW_700,
                1024: ft.Colors.AMBER_600,
                2048: ft.Colors.AMBER_900
            }
            return color_map.get(value, ft.Colors.PURPLE_300)
        
        # Convert state to 2D board
        board = np.array(state).reshape(self.SHAPE)
        display_board = [[int(2**int(x)) if int(x) > 0 else 0 for x in row] for row in board]
        
        # Create grid container
        board_container = ft.Column(spacing=5, alignment=ft.MainAxisAlignment.CENTER)
        
        for row in display_board:
            row_controls = []
            for cell in row:
                color = get_tile_color(cell)
                text_color = "white" if cell > 4 else "black"
                
                cell_container = ft.Container(
                    content=ft.Text(
                        str(cell) if cell > 0 else "",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=text_color,
                        text_align=ft.TextAlign.CENTER
                    ),
                    width=60,
                    height=60,
                    bgcolor=color,
                    border_radius=5,
                    alignment=ft.alignment.center,
                    border=ft.border.all(2, ft.Colors.GREY_400)
                )
                row_controls.append(cell_container)
            
            board_container.controls.append(
                ft.Row(row_controls, spacing=5, alignment=ft.MainAxisAlignment.CENTER)
            )
        
        return ft.Container(
            content=board_container,
            padding=20,
            bgcolor=ft.Colors.GREY_300,
            border_radius=10,
            alignment=ft.alignment.center
        )

    def create_game_buttons(self, visualizer):
        """Create 2048-specific buttons with horizontal layout and 2048 styling."""
        
        # Create directional move buttons with 2048-style colors
        move_buttons = []
        button_configs = [
            (0, '← Left', ft.Colors.DEEP_ORANGE_400),
            (1, 'Right →', ft.Colors.DEEP_ORANGE_400),
            (2, '↑ Up', ft.Colors.DEEP_ORANGE_400),
            (3, '↓ Down', ft.Colors.DEEP_ORANGE_400)
        ]
        
        for direction, text, bgcolor in button_configs:
            button = GameButton(
                text=text,
                on_click_fn=lambda e, d=direction: visualizer.on_move_button_click(d)(e),
                width=90,
                height=50,
                bgcolor=bgcolor,
                color=ft.Colors.WHITE
            )
            move_buttons.append(button)
        
        # Create control buttons with 2048 theme
        restart_button = GameButton(
            text="🔄 New 2048 Game",
            on_click_fn=visualizer.on_restart_button_click,
            bgcolor=ft.Colors.BLUE_GREY_600,
            color=ft.Colors.WHITE,
            width=160,
            height=50
        )
        
        luck_button = GameButton(
            text="🎯 Luck: OFF",
            on_click_fn=visualizer.on_luck_button_click,
            bgcolor=ft.Colors.AMBER_600,
            color=ft.Colors.WHITE,
            width=120,
            height=50
        )
        
        return {
            'move': move_buttons,
            'control': [restart_button, luck_button]
        }

