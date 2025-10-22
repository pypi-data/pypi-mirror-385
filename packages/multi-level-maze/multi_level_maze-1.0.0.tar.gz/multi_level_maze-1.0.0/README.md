# Multi-Level Maze Gymnasium Environment

**Multi-Level Maze** is a [Gymnasium](https://gymnasium.farama.org/) environment that generates hierarchical mazes using recursive spanning-tree connectivity.
Each maze consists of multiple levels of structure, where every sub-block is internally connected.

![Screenshot](./maze.png?raw=true "Screenshot")

---

## Getting Started

### Installation

You can install it using:

```bash
pip install multi-level-maze
```

Then, in your Python environment:

```python
import gymnasium as gym
import multi_level_maze

env = gym.make("MultiLevelMaze-v0", size=3, levels=3, maze_seed=2, max_steps=1000, cell_size=30)
obs, info = env.reset()

done, truncated = False, False
while not (done or truncated):
    env.render()
    action = env.action_space.sample()
    obs, reward, done, truncated, info = env.step(action)

env.close()
```

---

## Environment Parameters

You can customize the environment using the following arguments when creating it with `gym.make("MultiLevelMaze-v0", ...)`.

| Argument     | Type | Default | Description                                                                |
| ------------ | ---- | ------- | -------------------------------------------------------------------------- |
| `size`       | int  | 3       | Base grid size for each level. The total maze size is `size ** levels`.    |
| `levels`     | int  | 2       | Number of hierarchical levels (recursive subdivisions).                    |
| `max_steps`  | int  | 1000    | Maximum steps per episode before truncation.                               |
| `cell_size`  | int  | 50      | Pixel size of each maze cell in render mode.                               |
| `maze_seed`  | int  | 1       | Seed controlling the maze structure. Fixed per environment.                |
| `render_fps` | int  | 5       | Frames per second when rendering with Pygame.                              |

---

### Reproducibility

* The **maze structure** is fixed by `maze_seed` and reused across resets.
* The **starting position and goal** are randomized each time you call `reset(seed=...)`.
* Using the same `seed` reproduces the same starting and goal positions.
* To generate a completely new maze, reinstantiate the environment with a different `maze_seed`.

---

## Observations and Actions

**Observation Space:**
A concatenated vector of one-hot encodings representing the agent’s and goal’s positions at each hierarchical level.

**Action Space:**
Discrete with 4 actions:

| Action | Meaning    |
| ------ | ---------- |
| 0      | Move up    |
| 1      | Move down  |
| 2      | Move left  |
| 3      | Move right |

---

## Citation

If you use this environment in your research, please cite it using the `CITATION.cff` file included in this repository.

---

## License

```
Copyright (C) 2025 Ali Jahani

This program is free software; you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation; either version 3 of
the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program;
if not, see https://www.gnu.org/licenses.
```

---

## TODO

* [ ] **Vectorization**
