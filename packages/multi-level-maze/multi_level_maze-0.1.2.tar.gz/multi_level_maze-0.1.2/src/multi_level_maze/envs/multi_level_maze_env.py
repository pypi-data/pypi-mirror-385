import numpy as np
import pygame
import gymnasium as gym
from gymnasium import spaces

class MultiLevelMazeEnv(gym.Env):
    """
    Multi-Level Maze.
    The generator produces a global grid of size total_size = size ** levels. Connectivity
    is a spanning-tree-based construction that ensures:
      - each sub-block (at each recursion base) is internally connected (spanning tree),
      - sub-blocks are connected to each other via exactly one corridor per selected seam,
        and the set of seams chosen follows a spanning tree over the sub-block graph.

    Observation:
        concatenated one-hot vectors, one per level, where each level encodes position
        within that level's block, this is done for both our current position and goal.

    Actions: 0=up,1=down,2=left,3=right

    Args:
      size (int, default=3):
        Base size of each level’s grid. The total maze size is `size ** levels`.
        For example, with `size=3` and `levels=2`, the maze will be 9×9 cells.

      levels (int, default=2):
        Number of hierarchical levels. Each level recursively subdivides the grid,
        creating a larger maze with structured connectivity between sub-blocks.

      max_steps (int, default=1000):
        Maximum number of environment steps before truncation.

      cell_size (int, default=50):
        Pixel size of a single maze cell when rendering with pygame.

      maze_seed (int, default=1):
        Random seed used to generate the maze connectivity graph.

      render_fps (int, default=5):
        Target rendering frame rate (frames per second).
    """

    metadata = {
        "render_modes": ["human"],
        "render_fps": 5,
    }

    def __init__(self, size=3, levels=2, max_steps=1000, cell_size=50, maze_seed=1, render_fps=5):
        super().__init__()
        assert size >= 2 and levels >= 1
        self.size = size
        self.levels = levels
        self.total_size = size ** levels
        self.max_steps = max_steps
        self.cell_size = cell_size
        self.maze_rng = np.random.default_rng(maze_seed)
        self.metadata["render_fps"] = render_fps

        # action space
        self.action_space = spaces.Discrete(4)

        # observation: concatenated one-hot per level (size*size each)
        obs_len = levels * (size * size) * 2  # agent and goal concatenated
        self.observation_space = spaces.Box(low=0, high=1, shape=(obs_len,), dtype=np.float32)

        # adjacency: dict mapping (x,y) -> set of neighbor (nx,ny) coordinates
        self.adj = {}

        # state
        self.pos = None # (x,y)
        self.goal = None
        self.steps = 0
        self.maze_generated = False

        # rendering
        self.window = None
        self.clock = None

    def _grid_neighbors(self, p, size):
        """Return 4-neighbors inside bounds."""
        x, y = p
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size:
                yield (nx, ny)

    def _add_edge(self, a, b):
        """Add undirected edge between cells a and b."""
        if a not in self.adj:
            self.adj[a] = set()
        if b not in self.adj:
            self.adj[b] = set()
        self.adj[a].add(b)
        self.adj[b].add(a)

    def _make_empty_adj(self, total_n):
        """Initialize adjacency dict with all cells and empty neighbor sets."""
        self.adj = {}
        for i in range(total_n):
            for j in range(total_n):
                self.adj[(i, j)] = set()

    def _generate_connectivity(self, size, levels, origin_x=0, origin_y=0):
        """
        Recursively build adjacency for the block whose top-left is (origin_x, origin_y)
        and whose dimension is (size**levels) x (size**levels).
        """
        block_n = size ** levels

        # connect sub-blocks with a spanning tree over the sub-block grid;
        # for each chosen edge carve exactly one corridor between the two sub-blocks
        tmp_maze = np.zeros((size, size))
        rand_start = (self.maze_rng.integers(size), self.maze_rng.integers(size))
        tmp_maze[rand_start] = 1
        points = [rand_start]
        n = size ** (levels - 1) - 1
        while points:
            p = tuple(self.maze_rng.choice(points))
            possible_moves = []
            for neighbor in self._grid_neighbors(p, size):
                if tmp_maze[neighbor] != 1:
                    possible_moves.append(neighbor)

            if not possible_moves:
                points.remove(p)
                continue

            new_p = tuple(self.maze_rng.choice(possible_moves))
            points.append(new_p)
            tmp_maze[new_p] = 1
            # Depending on the size of connection between blocks, we have multiple choices.
            if levels > 1:
                picked_connection = self.maze_rng.integers(size ** (levels - 1) - 1)
                if new_p[0] != p[0]:
                    first_p = (min(new_p[0], p[0]) * (n+1) + n, p[1]*size*(levels-1)+picked_connection)
                    second_p = (first_p[0]+1, first_p[1])
                else:
                    first_p = (p[0]*size**(levels-1)+picked_connection, min(new_p[1], p[1]) * (n+1) + n)
                    second_p = (first_p[0], first_p[1]+1)
            else:
                first_p = p
                second_p = new_p
            first_p = (first_p[0]+origin_x, first_p[1]+origin_y)
            second_p = (second_p[0]+origin_x, second_p[1]+origin_y)
            self._add_edge(first_p, second_p)

        # recursively create each sub-block's connectivity
        if levels < 2:
            return

        sub_n = size ** (levels - 1)
        for bi in range(size):
            for bj in range(size):
                sub_origin_x = origin_x + bi * sub_n
                sub_origin_y = origin_y + bj * sub_n
                self._generate_connectivity(size, levels - 1, sub_origin_x, sub_origin_y)

    ###########
    # Gym API #
    ###########

    def reset(
        self,
        seed: int | None = None,
        options: dict | None = None,
    ):
        """
        Reset the environment to start a new episode.

        Args:
          seed (int | None, default=None):
            Random seed controlling reproducibility of agent start and goal positions.
            If `None`, a random seed is used.

          options (dict | None, default=None):
            Currently unused.

        Returns:
          observation (np.ndarray):
            Concatenated one-hot encoded vectors representing the agent’s and goal’s
            positions at all hierarchical levels.

          info (dict):
            Empty dictionary, included for API compatibility.
        """
        super().reset(seed=seed)
        rng = np.random.default_rng(seed)

        if not self.maze_generated:
            self._make_empty_adj(self.total_size)
            self._generate_connectivity(self.size, self.levels, origin_x=0, origin_y=0)
            self.maze_generated = True

        size = self.size ** self.levels
        self.pos = (rng.integers(size), rng.integers(size))
        while True:
            self.goal = (rng.integers(size), rng.integers(size))
            if self.goal != self.pos:
                break

        self.steps = 0
        return self._get_obs(), {}

    def _hierarchical_observation(self, point):
        gx, gy = point
        coords = []
        for _ in range(self.levels):
            coords.append((gx % self.size, gy % self.size))
            gx //= self.size
            gy //= self.size
        coords.reverse()
        flat = []
        for (x, y) in coords:
            one_hot = np.zeros(self.size * self.size, dtype=np.float32)
            one_hot[x * self.size + y] = 1
            flat.append(one_hot)
        return np.concatenate(flat)

    def _get_obs(self):
        self_pos = self._hierarchical_observation(self.pos)
        goal_pos = self._hierarchical_observation(self.goal)
        return np.concatenate([self_pos, goal_pos])

    def step(self, action):
        """Step through environment"""
        self.steps += 1
        dx = dy = 0
        if action == 0:
            dx = -1
        elif action == 1:
            dx = 1
        elif action == 2:
            dy = -1
        elif action == 3:
            dy = 1

        x, y = self.pos
        nx, ny = x + dx, y + dy
        candidate = (nx, ny)
        # move only if candidate is in adjacency list and there's an edge
        if candidate in self.adj and candidate in self.adj[(x, y)]:
            self.pos = candidate
        # otherwise stay in place

        terminated = (self.pos == self.goal)
        truncated = self.steps >= self.max_steps
        reward = 0 if terminated else -1
        return self._get_obs(), reward, terminated, truncated, {}

    def render(self, mode="human", show_openings_color=True):
        """
        Render that shows internal adjacency and also seam openings between blocks.
        Thick seam lines are drawn on block boundary.
        """
        if self.window is None:
            pygame.init()
            sz_px = self.total_size * self.cell_size
            self.window = pygame.display.set_mode((sz_px, sz_px))
            pygame.display.set_caption("Multi-Level Maze")
            self.clock = pygame.time.Clock()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.window = None
                return

        cs = self.cell_size
        # draw background
        self.window.fill((30, 30, 30))
        rect = pygame.Rect(0, 0, self.total_size * cs, self.total_size * cs)
        pygame.draw.rect(self.window, (240, 240, 240), rect)

        # draw agent and goal
        gx, gy = self.goal
        pygame.draw.rect(self.window, (255, 80, 80),
                         (gy * cs, gx * cs, cs, cs))
        px, py = self.pos
        pygame.draw.rect(self.window, (100, 200, 255),
                         (py * cs, px * cs, cs, cs))

        def fn(num, factor):
            out = 0
            num += 1
            while num % factor == 0:
                out += 1
                num /= factor
            return out

        # draw walls
        wall_color = (10, 10, 10)
        for i in range(self.total_size):
            for j in range(self.total_size):
                a = (i, j)
                b = (i, j + 1)
                thickness = fn(j, self.size) * 2 + 2
                if b not in self.adj.get(a, set()):
                    x = (j + 1) * cs
                    pygame.draw.line(self.window, wall_color, (x, i * cs), (x, (i + 1) * cs), thickness)

                b = (i + 1, j)
                thickness = fn(i, self.size) * 2 + 2
                if b not in self.adj.get(a, set()):
                    y = (i + 1) * cs
                    pygame.draw.line(self.window, wall_color, (j * cs, y), ((j + 1) * cs, y), thickness)

        pygame.display.flip()
        self.clock.tick(self.metadata["render_fps"])

    def close(self):
        if self.window:
            pygame.quit()
            self.window = None
