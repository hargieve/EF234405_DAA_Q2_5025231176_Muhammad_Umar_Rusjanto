"""
Maze Pathfinder Game — Dijkstra's Algorithm Visualization
EF234405 Design & Analysis of Algorithms — Quiz 2
"""

import pygame
import heapq
import random
import time
import sys
from enum import Enum

# ─── Constants ─────────────────────────────────────────────────────────────────
WINDOW_W, WINDOW_H = 1100, 720
SIDE_PANEL_W = 260
GRID_AREA_W = WINDOW_W - SIDE_PANEL_W

COLS, ROWS = 31, 21          # must be odd for recursive-division maze
CELL = GRID_AREA_W // COLS   # cell pixel size

FPS = 60
VIZ_DELAY = 18               # ms between each Dijkstra step in animation

# ─── Colours ───────────────────────────────────────────────────────────────────
BG          = (10,  12,  20)
WALL_COL    = (18,  22,  40)
WALL_BORDER = (30,  40,  70)
FREE_COL    = (28,  34,  58)
VISITED_COL = (20,  80, 120)
FRONTIER_COL= (40, 160, 200)
PATH_COL    = (255, 210,  50)
START_COL   = (50,  220, 100)
END_COL     = (220,  60,  80)
GRID_LINE   = (20,  26,  48)
PANEL_BG    = (14,  16,  30)
TEXT_WHITE  = (220, 230, 255)
TEXT_DIM    = (100, 120, 160)
ACCENT      = (80,  160, 255)
COST_COL    = (60, 200, 160)

# ─── Cell types ────────────────────────────────────────────────────────────────
class Cell(Enum):
    WALL     = 0
    FREE     = 1
    VISITED  = 2
    FRONTIER = 3
    PATH     = 4
    START    = 5
    END      = 6


# ══════════════════════════════════════════════════════════════════════════════
#  Maze generator — Recursive Division (produces nice corridors)
# ══════════════════════════════════════════════════════════════════════════════
def generate_maze(cols: int, rows: int) -> list[list[Cell]]:
    """Returns a 2‑D grid of Cell values with a guaranteed solvable maze."""
    grid = [[Cell.FREE for _ in range(cols)] for _ in range(rows)]

    # Border walls
    for r in range(rows):
        for c in range(cols):
            if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
                grid[r][c] = Cell.WALL

    def divide(r1, c1, r2, c2):
        """Recursively divide the region [r1..r2] x [c1..c2] with walls."""
        height = r2 - r1
        width  = c2 - c1
        if height < 2 or width < 2:
            return

        # Choose orientation: prefer dividing the longer axis
        horizontal = (height > width) or (height == width and random.random() < 0.5)

        if horizontal:
            # Pick an even row to place wall
            wall_rows = [r for r in range(r1 + 1, r2) if r % 2 == 0]
            if not wall_rows:
                return
            wr = random.choice(wall_rows)
            # Pick odd column for the gap
            gap_cols = [c for c in range(c1, c2 + 1) if c % 2 == 1]
            gc = random.choice(gap_cols) if gap_cols else (c1 + c2) // 2
            for c in range(c1, c2 + 1):
                if c != gc:
                    grid[wr][c] = Cell.WALL
            divide(r1, c1, wr - 1, c2)
            divide(wr + 1, c1, r2, c2)
        else:
            wall_cols = [c for c in range(c1 + 1, c2) if c % 2 == 0]
            if not wall_cols:
                return
            wc = random.choice(wall_cols)
            gap_rows = [r for r in range(r1, r2 + 1) if r % 2 == 1]
            gr = random.choice(gap_rows) if gap_rows else (r1 + r2) // 2
            for r in range(r1, r2 + 1):
                if r != gr:
                    grid[r][wc] = Cell.WALL
            divide(r1, c1, r2, wc - 1)
            divide(r1, wc + 1, r2, c2)

    divide(1, 1, rows - 2, cols - 2)
    return grid


# ══════════════════════════════════════════════════════════════════════════════
#  Weighted graph helper — random weights on passable edges for Dijkstra realism
# ══════════════════════════════════════════════════════════════════════════════
def build_weights(grid, cols, rows):
    """Assign a random integer weight 1-9 to every passable cell."""
    weights = {}
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != Cell.WALL:
                weights[(r, c)] = random.randint(1, 9)
    return weights


# ══════════════════════════════════════════════════════════════════════════════
#  Dijkstra's Algorithm — yields intermediate states for animation
# ══════════════════════════════════════════════════════════════════════════════
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def dijkstra(grid, weights, start, end, cols, rows):
    """
    Generator: yields (visited_set, frontier_set, dist_dict, prev_dict) at
    each relaxation step so the UI can animate it.
    Yields None when done; final state holds the answer.
    """
    dist = {start: 0}
    prev = {}
    visited = set()
    # heap: (cost, row, col)
    heap = [(0, start[0], start[1])]

    while heap:
        cost, r, c = heapq.heappop(heap)
        node = (r, c)

        if node in visited:
            continue
        visited.add(node)

        frontier = {(nr, nc) for _, nr, nc in heap
                    if grid[nr][nc] != Cell.WALL and (nr, nc) not in visited}

        yield visited.copy(), frontier, dict(dist), dict(prev)

        if node == end:
            return

        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != Cell.WALL:
                neighbour = (nr, nc)
                edge_w = weights.get(neighbour, 1)
                new_cost = cost + edge_w
                if new_cost < dist.get(neighbour, float('inf')):
                    dist[neighbour] = new_cost
                    prev[neighbour] = node
                    heapq.heappush(heap, (new_cost, nr, nc))

    yield visited.copy(), set(), dict(dist), dict(prev)


def reconstruct_path(prev, start, end):
    path = []
    cur = end
    while cur in prev:
        path.append(cur)
        cur = prev[cur]
    path.append(start)
    path.reverse()
    return path if path[0] == start else []


# ══════════════════════════════════════════════════════════════════════════════
#  Drawing helpers
# ══════════════════════════════════════════════════════════════════════════════
def cell_rect(r, c):
    return pygame.Rect(c * CELL, r * CELL, CELL, CELL)


def draw_grid(surf, grid, weights, visited, frontier, path, start, end, show_weights):
    for r in range(ROWS):
        for c in range(COLS):
            node = (r, c)
            rect = cell_rect(r, c)
            cell = grid[r][c]

            # Background colour
            if cell == Cell.WALL:
                colour = WALL_COL
            elif node == start:
                colour = START_COL
            elif node == end:
                colour = END_COL
            elif node in path:
                colour = PATH_COL
            elif node in visited:
                colour = VISITED_COL
            elif node in frontier:
                colour = FRONTIER_COL
            else:
                colour = FREE_COL

            pygame.draw.rect(surf, colour, rect)

            # Weight label on passable cells
            if show_weights and cell != Cell.WALL and node not in (start, end):
                w = weights.get(node, 1)
                label = pygame.font.SysFont("consolas", 9).render(str(w), True,
                        (60, 80, 110) if node not in path else (30, 30, 30))
                surf.blit(label, (rect.x + 2, rect.y + 2))

            # Cell border
            if cell == Cell.WALL:
                pygame.draw.rect(surf, WALL_BORDER, rect, 1)
            else:
                pygame.draw.rect(surf, GRID_LINE, rect, 1)

    # Highlight start / end with an icon
    for node, col, symbol in [(start, START_COL, "S"), (end, END_COL, "E")]:
        r, c = node
        rect = cell_rect(r, c)
        font = pygame.font.SysFont("consolas", CELL - 4, bold=True)
        lbl = font.render(symbol, True, BG)
        surf.blit(lbl, lbl.get_rect(center=rect.center))


def draw_panel(surf, state_info, elapsed, path_cost, path_len, nodes_visited,
               show_weights, animating, font_big, font_med, font_sm):
    px = GRID_AREA_W
    panel = pygame.Rect(px, 0, SIDE_PANEL_W, WINDOW_H)
    pygame.draw.rect(surf, PANEL_BG, panel)
    pygame.draw.line(surf, ACCENT, (px, 0), (px, WINDOW_H), 2)

    y = 24
    def text(txt, font, colour, cx=None, lx=None):
        nonlocal y
        lx = lx or px + 18
        s = font.render(txt, True, colour)
        surf.blit(s, (lx, y))
        y += s.get_height() + 4

    # Title
    text("MAZE", font_big, ACCENT, lx=px + 18)
    y -= 8
    text("PATHFINDER", font_big, TEXT_WHITE, lx=px + 18)
    y += 6
    text("Dijkstra's Algorithm", font_sm, TEXT_DIM, lx=px + 18)

    # Divider
    y += 10
    pygame.draw.line(surf, (40, 50, 80), (px + 14, y), (px + SIDE_PANEL_W - 14, y))
    y += 14

    # Stats
    def stat(label, val, col=TEXT_WHITE):
        nonlocal y
        lbl = font_sm.render(label, True, TEXT_DIM)
        val_s = font_med.render(str(val), True, col)
        surf.blit(lbl, (px + 18, y))
        surf.blit(val_s, (px + SIDE_PANEL_W - val_s.get_width() - 14, y))
        y += max(lbl.get_height(), val_s.get_height()) + 6

    stat("Status", state_info, ACCENT if animating else (100, 220, 120))
    stat("Time elapsed", f"{elapsed:.2f}s", TEXT_WHITE)
    stat("Nodes visited", str(nodes_visited), VISITED_COL)
    stat("Path cost", str(path_cost) if path_cost else "—", PATH_COL)
    stat("Path length", str(path_len) if path_len else "—", PATH_COL)
    stat("Grid size", f"{COLS}×{ROWS}", TEXT_DIM)

    y += 10
    pygame.draw.line(surf, (40, 50, 80), (px + 14, y), (px + SIDE_PANEL_W - 14, y))
    y += 14

    # Legend
    text("LEGEND", font_sm, TEXT_DIM)
    y += 2
    legend = [
        (START_COL,    "Start node"),
        (END_COL,      "End node"),
        (VISITED_COL,  "Visited"),
        (FRONTIER_COL, "Frontier"),
        (PATH_COL,     "Shortest path"),
        (WALL_COL,     "Wall"),
    ]
    for col, lbl in legend:
        pygame.draw.rect(surf, col, (px + 18, y + 2, 14, 14))
        s = font_sm.render(lbl, True, TEXT_WHITE)
        surf.blit(s, (px + 38, y))
        y += 20

    y += 10
    pygame.draw.line(surf, (40, 50, 80), (px + 14, y), (px + SIDE_PANEL_W - 14, y))
    y += 14

    # Controls
    text("CONTROLS", font_sm, TEXT_DIM)
    controls = [
        ("[SPACE]", "Run / Pause"),
        ("[R]",     "New maze"),
        ("[W]",     "Toggle weights"),
        ("[S]",     "Skip animation"),
        ("[ESC]",   "Quit"),
    ]
    for key, desc in controls:
        ks = font_sm.render(key, True, ACCENT)
        ds = font_sm.render(desc, True, TEXT_WHITE)
        surf.blit(ks, (px + 18, y))
        surf.blit(ds, (px + 18 + ks.get_width() + 6, y))
        y += ks.get_height() + 5

    y += 8
    # Weight toggle indicator
    wt = font_sm.render(f"Weights: {'ON' if show_weights else 'OFF'}",
                        True, COST_COL if show_weights else TEXT_DIM)
    surf.blit(wt, (px + 18, y))


# ══════════════════════════════════════════════════════════════════════════════
#  Main game loop
# ══════════════════════════════════════════════════════════════════════════════
def find_free_cell(grid, near_row, near_col):
    """Find nearest free cell to the given position."""
    for dr in range(ROWS):
        for dc in range(COLS):
            for sr, sc in [(near_row+dr, near_col+dc),(near_row-dr, near_col+dc),
                           (near_row+dr, near_col-dc),(near_row-dr, near_col-dc)]:
                if 0 <= sr < ROWS and 0 <= sc < COLS and grid[sr][sc] == Cell.FREE:
                    return (sr, sc)
    return (1, 1)


def new_game():
    grid = generate_maze(COLS, ROWS)
    weights = build_weights(grid, COLS, ROWS)
    start = find_free_cell(grid, 1, 1)
    end   = find_free_cell(grid, ROWS - 2, COLS - 2)
    if start == end:
        end = find_free_cell(grid, ROWS // 2, COLS - 2)
    return grid, weights, start, end


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Maze Pathfinder — Dijkstra's Algorithm")
    clock = pygame.time.Clock()

    font_big = pygame.font.SysFont("consolas", 22, bold=True)
    font_med = pygame.font.SysFont("consolas", 15, bold=True)
    font_sm  = pygame.font.SysFont("consolas", 13)

    grid, weights, start, end = new_game()

    # Algorithm state
    gen          = None
    visited      = set()
    frontier     = set()
    dist_map     = {}
    prev_map     = {}
    path         = []
    animating    = False
    done         = False
    show_weights = False
    last_step    = 0
    start_time   = None
    elapsed      = 0.0
    nodes_visited= 0
    path_cost    = 0
    path_len     = 0
    status       = "Ready"

    running = True
    while running:
        now = pygame.time.get_ticks()

        # ── Events ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_r:
                    # New maze
                    grid, weights, start, end = new_game()
                    gen = None; visited.clear(); frontier.clear()
                    dist_map.clear(); prev_map.clear(); path.clear()
                    animating = False; done = False
                    elapsed = 0.0; nodes_visited = 0
                    path_cost = 0; path_len = 0; status = "Ready"

                elif event.key == pygame.K_w:
                    show_weights = not show_weights

                elif event.key == pygame.K_SPACE:
                    if done:
                        pass  # already finished
                    elif not animating:
                        # Start / resume
                        if gen is None:
                            gen = dijkstra(grid, weights, start, end, COLS, ROWS)
                            start_time = time.time()
                        animating = True
                        status = "Running…"
                    else:
                        animating = False
                        status = "Paused"

                elif event.key == pygame.K_s:
                    # Skip to completion instantly
                    if gen is None:
                        gen = dijkstra(grid, weights, start, end, COLS, ROWS)
                        start_time = time.time()
                    for state in gen:
                        visited, frontier, dist_map, prev_map = state
                    gen = None; animating = False; done = True
                    elapsed = time.time() - start_time
                    path = reconstruct_path(prev_map, start, end)
                    nodes_visited = len(visited)
                    path_cost = dist_map.get(end, 0)
                    path_len = len(path)
                    status = "Done!" if path else "No path found"

        # ── Step animation ───────────────────────────────────────────────────
        if animating and gen is not None and (now - last_step) >= VIZ_DELAY:
            last_step = now
            try:
                visited, frontier, dist_map, prev_map = next(gen)
                nodes_visited = len(visited)
                elapsed = time.time() - start_time
            except StopIteration:
                gen = None; animating = False; done = True
                elapsed = time.time() - start_time
                path = reconstruct_path(prev_map, start, end)
                path_cost = dist_map.get(end, 0)
                path_len = len(path)
                status = "Done!" if path else "No path found"

        # ── Render ───────────────────────────────────────────────────────────
        screen.fill(BG)

        # Grid surface (clipped)
        grid_surf = pygame.Surface((GRID_AREA_W, WINDOW_H))
        grid_surf.fill(BG)
        draw_grid(grid_surf, grid, weights,
                  visited, frontier, path, start, end, show_weights)
        screen.blit(grid_surf, (0, 0))

        # Side panel
        draw_panel(screen, status, elapsed, path_cost, path_len, nodes_visited,
                   show_weights, animating, font_big, font_med, font_sm)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()