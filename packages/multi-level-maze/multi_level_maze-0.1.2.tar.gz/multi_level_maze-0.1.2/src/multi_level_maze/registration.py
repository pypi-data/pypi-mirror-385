from gymnasium.envs.registration import register

register(
    id="MultiLevelMaze-v0",
    entry_point="multi_level_maze.envs.multi_level_maze_env:MultiLevelMazeEnv",
)
