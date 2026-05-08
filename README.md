# Maze Pathfinder — Dijkstra's Algorithm

**EF234405 Design & Analysis of Algorithms — Quiz 2**  
**Muhammad Umar Rusjanto | 5025231176 | IUP Class**

## Overview
An interactive maze game built with Python & pygame that generates a random weighted maze using **Recursive Division** and finds the shortest path using **Dijkstra's Algorithm**. Each passable cell carries a random weight (1–9), making this a true weighted shortest-path problem.

## Features
- Procedural maze generation via Recursive Division
- Weighted graph with random cell costs (1–9)
- Step-by-step animation of Dijkstra's exploration
- Live statistics: nodes visited, path cost, path length, elapsed time
- Keyboard controls for interactivity

## Requirements
```bash
pip install pygame
```

## How to Run
```bash
py -3.12 maze_pathfinder/maze_pathfinder.py
```

## Controls
| Key | Action |
|-----|--------|
| `SPACE` | Run / Pause the algorithm |
| `R` | Generate a new random maze |
| `W` | Toggle weight labels on cells |
| `S` | Skip to final result instantly |
| `ESC` | Quit |

## Algorithm
Dijkstra's algorithm with a binary min-heap prioritizes the lowest-cost node at each step, guaranteeing the optimal shortest path in a weighted graph.

**Time complexity: O((V + E) log V)**

## Graph Model
- **Nodes** — each passable cell in the maze
- **Edges** — horizontal/vertical adjacency between passable cells  
- **Weights** — random integer 1–9 assigned to each destination cell

## File Structure
```
EF234405_DAA_Q2_5025231176_Muhammad_Umar_Rusjanto/
└── maze_pathfinder/
    └── maze_pathfinder.py
```
