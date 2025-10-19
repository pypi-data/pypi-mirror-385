import ast
import json
import os

import jax.numpy as jnp
from flax.core.frozen_dict import FrozenDict

from meal.env.common import WALL, GOAL, ONION_PILE, PLATE_PILE, POT, AGENT
from meal.env.generation.layout_validator import INTERACTIVE_TILES

cramped_room = {
    "height": 4,
    "width": 5,
    "wall_idx": jnp.array([0, 1, 2, 3, 4,
                           5, 9,
                           10, 14,
                           15, 16, 17, 18, 19]),
    "agent_idx": jnp.array([6, 8]),
    "goal_idx": jnp.array([18]),
    "plate_pile_idx": jnp.array([16]),
    "onion_pile_idx": jnp.array([5, 9]),
    "pot_idx": jnp.array([2])
}
asymm_advantages = {
    "height": 5,
    "width": 9,
    "wall_idx": jnp.array([0, 1, 2, 3, 4, 5, 6, 7, 8,
                           9, 11, 12, 13, 14, 15, 17,
                           18, 22, 26,
                           27, 31, 35,
                           36, 37, 38, 39, 40, 41, 42, 43, 44]),
    "agent_idx": jnp.array([29, 32]),
    "goal_idx": jnp.array([12, 17]),
    "plate_pile_idx": jnp.array([39, 41]),
    "onion_pile_idx": jnp.array([9, 14]),
    "pot_idx": jnp.array([22, 31])
}
coord_ring = {
    "height": 5,
    "width": 5,
    "wall_idx": jnp.array([0, 1, 2, 3, 4,
                           5, 9,
                           10, 12, 14,
                           15, 19,
                           20, 21, 22, 23, 24]),
    "agent_idx": jnp.array([7, 11]),
    "goal_idx": jnp.array([22]),
    "plate_pile_idx": jnp.array([10]),
    "onion_pile_idx": jnp.array([15, 21]),
    "pot_idx": jnp.array([3, 9])
}
forced_coord = {
    "height": 5,
    "width": 5,
    "wall_idx": jnp.array([0, 1, 2, 3, 4,
                           5, 7, 9,
                           10, 12, 14,
                           15, 17, 19,
                           20, 21, 22, 23, 24]),
    "agent_idx": jnp.array([11, 8]),
    "goal_idx": jnp.array([23]),
    "onion_pile_idx": jnp.array([5, 10]),
    "plate_pile_idx": jnp.array([15]),
    "pot_idx": jnp.array([3, 9])
}

# Example of layout provided as a grid
counter_circuit_grid = """
WWWPPWWW
W A    W
B WWWW X
W     AW
WWWOOWWW
"""

square_arena = """
WWWWWWW
W  P  W
W A A W
WO   BW
W  X  W
WWWWWWW
"""


def layout_grid_to_dict(grid):
    """Convert grid string to the JAX‑MARL FrozenDict layout representation.

    Supports two symbol sets:
    1. Legacy symbols: W (wall), A (agent), X (goal), B (plate pile), O (onion pile), P (pot), ' ' (empty)
    2. Constants from meal.env.common: WALL, AGENT, GOAL, PLATE_PILE, ONION_PILE, POT, FLOOR
    """
    # Handle both string input and strip whitespace
    if hasattr(grid, 'strip'):
        rows = grid.strip().split('\n')
    else:
        rows = grid.split('\n')

    # Remove empty rows at start/end
    if len(rows) > 0 and len(rows[0]) == 0:
        rows = rows[1:]
    if len(rows) > 0 and len(rows[-1]) == 0:
        rows = rows[:-1]

    height, width = len(rows), len(rows[0]) if rows else 0
    keys = ["wall_idx", "agent_idx", "goal_idx", "plate_pile_idx", "onion_pile_idx", "pot_idx"]

    # Support both legacy symbols and constants from meal.env.common
    symbol_to_key = {
        # Legacy symbols
        "W": "wall_idx",
        "A": "agent_idx",
        "X": "goal_idx",
        "B": "plate_pile_idx",
        "O": "onion_pile_idx",
        "P": "pot_idx",
        # Constants from meal.env.common
        WALL: "wall_idx",
        AGENT: "agent_idx",
        GOAL: "goal_idx",
        PLATE_PILE: "plate_pile_idx",
        ONION_PILE: "onion_pile_idx",
        POT: "pot_idx",
    }

    layout_dict = {key: [] for key in keys}
    layout_dict["height"] = height
    layout_dict["width"] = width

    for i, row in enumerate(rows):
        for j, obj in enumerate(row):
            flat_idx = width * i + j
            if obj in symbol_to_key:
                layout_dict[symbol_to_key[obj]].append(flat_idx)

            # Interactive tiles count as walls for Overcooked's pathing
            # Legacy symbols that are interactive
            if obj in ["X", "B", "O", "P"]:
                layout_dict["wall_idx"].append(flat_idx)
            # Constants from meal.env.common that are interactive or walls
            elif obj in INTERACTIVE_TILES | {WALL}:
                layout_dict["wall_idx"].append(flat_idx)

    # Convert to JAX arrays
    for key in keys:
        layout_dict[key] = jnp.array(layout_dict[key], dtype=jnp.int32)

    return FrozenDict(layout_dict)


def _parse_layout_string(layout_str: str) -> FrozenDict:
    """Parse a string representation of a FrozenDict layout back to actual FrozenDict."""
    # Remove the "FrozenDict(" prefix and ")" suffix
    if layout_str.startswith("FrozenDict("):
        layout_str = layout_str[11:-1]

    # Parse the dictionary-like string
    # Replace Array(...) with list representation for parsing
    import re

    # Extract array contents and convert to lists
    def array_replacer(match):
        array_content = match.group(1)

        # Find the array values part (everything between [ and ], before dtype=)
        # Handle multi-line arrays
        bracket_match = re.search(r'\[(.*?)\]', array_content, re.DOTALL)
        if bracket_match:
            values_str = bracket_match.group(1)
            # Clean up whitespace and newlines
            values_str = re.sub(r'\s+', ' ', values_str).strip()
            # Split by comma and convert to integers
            try:
                values = [int(x.strip()) for x in values_str.split(',') if x.strip()]
                return str(values)
            except ValueError:
                # If parsing fails, return empty list
                return "[]"
        else:
            return "[]"

    # Replace Array(...) patterns with lists - use DOTALL flag for multi-line matching
    layout_str = re.sub(r'Array\(([^)]+(?:\([^)]*\))*[^)]*)\)', array_replacer, layout_str, flags=re.DOTALL)

    # Add quotes around dictionary keys to make it valid Python syntax
    key_pattern = r'\b(wall_idx|agent_idx|goal_idx|plate_pile_idx|onion_pile_idx|pot_idx|height|width)\b:'
    layout_str = re.sub(key_pattern, r'"\1":', layout_str)

    # Parse the cleaned string as a dictionary
    try:
        layout_dict = ast.literal_eval(layout_str)
    except (ValueError, SyntaxError) as e:
        print(f"Failed to parse layout string: {e}")
        print(f"Cleaned string: {layout_str[:200]}...")
        # If parsing fails, create a minimal valid layout
        layout_dict = {
            "height": 6,
            "width": 7,
            "wall_idx": [],
            "agent_idx": [],
            "goal_idx": [],
            "plate_pile_idx": [],
            "onion_pile_idx": [],
            "pot_idx": []
        }

    # Convert lists to JAX arrays with correct dtypes
    array_keys = ["wall_idx", "agent_idx", "goal_idx", "plate_pile_idx", "onion_pile_idx", "pot_idx"]
    for key in array_keys:
        if key in layout_dict:
            layout_dict[key] = jnp.array(layout_dict[key], dtype=jnp.int32)
        else:
            layout_dict[key] = jnp.array([], dtype=jnp.int32)

    return FrozenDict(layout_dict)


def _load_layouts_from_json(json_file_path: str) -> dict:
    """Load layouts from a JSON file and convert them to FrozenDict format."""
    if not os.path.exists(json_file_path):
        print(f"Warning: JSON file {json_file_path} not found")
        return {}

    try:
        with open(json_file_path, 'r') as f:
            raw_data = json.load(f)

        layouts = {}
        for i, item in enumerate(raw_data):
            if isinstance(item, dict) and "layout" in item:
                # Parse the layout string to FrozenDict
                layout_str = item["layout"]
                if isinstance(layout_str, str):
                    parsed_layout = _parse_layout_string(layout_str)
                    # Generate a name based on file and index
                    base_name = os.path.splitext(os.path.basename(json_file_path))[0]
                    layout_name = f"{base_name}_{i}"
                    layouts[layout_name] = parsed_layout
                else:
                    # Already a proper layout object
                    base_name = os.path.splitext(os.path.basename(json_file_path))[0]
                    layout_name = f"{base_name}_{i}"
                    layouts[layout_name] = item["layout"]

        return layouts
    except Exception as e:
        print(f"Error loading layouts from {json_file_path}: {e}")
        return {}


def evaluate_grid(grid):
    '''
    Evaluate the validity of a grid layout based on a list of conditions
    '''

    valid = True

    # Check if the grid's rows are of equal length
    rows = grid.strip().split('\n')
    width = len(rows[0])
    for row in rows:
        if len(row) != width:
            valid = False

    # check if the grid has at least one of each required symbol
    required_symbols = ['W', 'X', 'O', 'B', 'P', 'A']
    for symbol in required_symbols:
        if symbol not in grid:
            valid = False

    if grid.count('A') != 2:
        valid = False

    # check if the grid is completely enclosed by walls
    valid_walls = ['W', 'X', 'B', 'O', 'P']

    for idx, row in enumerate(rows):
        if idx == 0 or idx == len(rows) - 1:
            for char in row:
                if char not in valid_walls:
                    valid = False
        if row[0] not in valid_walls or row[-1] not in valid_walls:
            valid = False

    # transform the grid into a matrix
    grid_matrix = [list(row) for row in rows]

    elements = ['A', 'X', 'O', 'B', 'P']
    positions = []
    for i, row in enumerate(grid_matrix):
        for j, char in enumerate(row):
            if char in elements:
                positions.append((i, j, char))

    # check if no elements are enclosed
    for i, j, char in positions:
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        reachable = False
        for dx, dy in directions:
            x, y = i + dx, j + dy
            if 0 <= x < len(grid_matrix) and 0 <= y < len(grid_matrix[0]):
                neighbor = grid_matrix[x][y]
                if neighbor == ' ' or neighbor == 'A':
                    reachable = True
                    break  # No need to check other directions
        if not reachable:
            valid = False

    # Check the reachability of the agents

    # Step 1: find the location of the agents
    agent_positions = []
    for i, row in enumerate(grid_matrix):
        for j, char in enumerate(row):
            if char == 'A':
                agent_positions.append((i, j))

    # Step 2: determine the reachability of the agents
    # For Agent 1
    visited1 = [[False for _ in range(len(grid_matrix[0]))] for _ in range(len(grid_matrix))]
    reachable_agent_1 = []
    dfs(agent_positions[0][0], agent_positions[0][1], grid_matrix, visited1, reachable_agent_1)

    # For Agent 2
    visited2 = [[False for _ in range(len(grid_matrix[0]))] for _ in range(len(grid_matrix))]
    reachable_agent_2 = []
    dfs(agent_positions[1][0], agent_positions[1][1], grid_matrix, visited2, reachable_agent_2)

    # Step 3: check if all elements are reachable
    elements_to_check = ['X', 'O', 'B', 'P']

    # For Agent 1
    agent1_reachable = {element: False for element in elements_to_check}
    for x, y, char in reachable_agent_1:
        if char in elements_to_check:
            agent1_reachable[char] = True

    # For Agent 2
    agent2_reachable = {element: False for element in elements_to_check}
    for x, y, char in reachable_agent_2:
        if char in elements_to_check:
            agent2_reachable[char] = True

    # Check if both agents can reach all elements
    if all(agent1_reachable.values()) and all(agent2_reachable.values()):
        pass  # Both agents can reach all elements
    else:
        # Check if collectively they can reach all elements
        elements_reachable = {element: agent1_reachable[element] or agent2_reachable[element] for element in
                              elements_to_check}
        if all(elements_reachable.values()):
            # Now check for a shared wall
            positions_agent1 = set((x, y) for x, y, char in reachable_agent_1)
            positions_agent2 = set((x, y) for x, y, char in reachable_agent_2)

            wall_positions = set()
            for i in range(len(grid_matrix)):
                for j in range(len(grid_matrix[0])):
                    if grid_matrix[i][j] == 'W':
                        wall_positions.add((i, j))

            shared_wall = False
            for i, j in wall_positions:
                neighbors_agent1 = False
                neighbors_agent2 = False
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                for dx, dy in directions:
                    x1, y1 = i + dx, j + dy
                    if (x1, y1) in positions_agent1:
                        neighbors_agent1 = True
                    if (x1, y1) in positions_agent2:
                        neighbors_agent2 = True
                if neighbors_agent1 and neighbors_agent2:
                    shared_wall = True
                    break

            if not shared_wall:
                valid = False
        else:
            valid = False

    return valid


def dfs(i, j, grid_matrix, visited, reachable):
    '''
    Depth-first search algorithm to check the reachability of the agents
    '''
    if i < 0 or i >= len(grid_matrix) or j < 0 or j >= len(grid_matrix[0]):
        return
    if visited[i][j]:
        return
    visited[i][j] = True
    element = grid_matrix[i][j]
    reachable.append((i, j, element))
    walkable = [' ', 'A']
    if element not in walkable:
        return
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for dx, dy in directions:
        dfs(i + dx, j + dy, grid_matrix, visited, reachable)


# Create new environments
split_kitchen = """
WWPWWWW
W A   W
W  W  W
WWWWXWW
W  W  W
W   A W
WWBOOWW
"""

basic_kitchen_large = """
WWWWWWW
P     O 
W     W
W  A  W
W  A  W
X     W
WWBWWWW
"""

basic_kitchen_small = """
WWWW
P  O
W  W
WAAW
X  B
WWWW
"""

shared_wall = """
WWWWWWWW
W  A   W
W      W
WPOBXWWW
W      W
W A    W
WWWWWWWW
"""

smallest_kitchen = """
WXWW
B AW
OA P
WWWW
"""

easy_layout = """
WWWWWW
O  A W
P  A W
B    W
W  X W
WWWWWW
"""

big_kitchen = """
WWWWWWWWWW
W        W
W  A  A  W
W        W
W  P  B  W
W        W
W  X  O  W
W        W
WWWWWWWWWW
"""

no_cooperation = """
WWWWWW
W  A W
WXBOPW
W  A W
WWWWWW
"""

foorced_coord_2 = """
WWWWWWWWW
W A W  AW
O   W   X
B   W   P
W   W   W
WWWWWWWWW
"""

basic_cooperative = """
WWWWWWWWW
WPOAW   W
W WW    W
W       W
W       W
W   AWXBW
WWWWWWWWW
"""

corridor_challenge = """
WWWWWWWWWWW
WA        W
WWWWWWWW  W
WP       XW
WO  WWWW  W
WB        W
WWWWWWW   W
W       A W
WWWWWWWWWWW
"""

split_work = """
WWPWWOWWW
WA      W
W       W
WWWW WWWW
W       W
W       W
WB     AW
WWWWXWWWW
"""

resource_sharing = """
WWPWWOWWW
WA      W
W  WWW  W
W  W    W
W  W    W
W  WWW  W
WB     AW
WWWWXWWWW
"""

efficiency_test = """
WWWWWWWWW
WA  P   W
W       W
WO WWW BW
W   W   W
W   W   W
WA  X   W
WWWWWWWWW
"""

c_kitchen = """
WWWWWPWWWW
WA       W
W  WWW   W
W  W     W
WO W    XW
W  WWW   W
WB      AW
WWWWWWWWWW
"""

vertical_corridors = """
WWWWW
WAOAW
W P W
W P W
W B W
W X W
WWWWW
"""

horizontal_corridors = """
WWWWWWW
WA    W
WOPPBXW
WA    W
WWWWWWW
"""

bottleneck_small = """
WWWWWWWW
W AP  OW
W      W
W WWWWWW
W      W
WB A XWW
WWWWWWWW
"""
bottleneck_large = """
WWWWWWWWWWW
WA  P    OW
W         W
WWWW WWWWWW
W         W
W         W
WB       XW
W     A   W
WWWWWWWWWWW
"""

# Load generated layouts from JSON files
_current_dir = os.path.dirname(os.path.abspath(__file__))
easy_generated_layouts = _load_layouts_from_json(os.path.join(_current_dir, "gen_20_easy.json"))
medium_generated_layouts = _load_layouts_from_json(os.path.join(_current_dir, "gen_20_medium.json"))
hard_generated_layouts = _load_layouts_from_json(os.path.join(_current_dir, "gen_20_hard.json"))

# Hard layouts
hard_layouts_legacy = {
    "forced_coord": FrozenDict(forced_coord),
    "forced_coord_2": layout_grid_to_dict(foorced_coord_2),
    "split_kitchen": layout_grid_to_dict(split_kitchen),
    "basic_cooperative": layout_grid_to_dict(basic_cooperative),
}

# Combine legacy and generated hard layouts
hard_layouts = {
    **hard_layouts_legacy,
    **hard_generated_layouts,
}

# Medium layouts
medium_layouts_legacy = {
    "coord_ring": FrozenDict(coord_ring),
    "efficiency_test": layout_grid_to_dict(efficiency_test),
    "split_work": layout_grid_to_dict(split_work),
    "bottleneck_small": layout_grid_to_dict(bottleneck_small),
    "bottleneck_large": layout_grid_to_dict(bottleneck_large),
    "counter_circuit": layout_grid_to_dict(counter_circuit_grid),
    "corridor_challenge": layout_grid_to_dict(corridor_challenge),
    "c_kitchen": layout_grid_to_dict(c_kitchen),
}

# Combine legacy and generated medium layouts
medium_layouts = {
    **medium_layouts_legacy,
    **medium_generated_layouts,
}

# Easy layouts
easy_layouts_legacy = {
    "cramped_room": FrozenDict(cramped_room),
    "asymm_advantages": FrozenDict(asymm_advantages),
    "square_arena": layout_grid_to_dict(square_arena),
    "basic_kitchen_small": layout_grid_to_dict(basic_kitchen_small),
    "shared_wall": layout_grid_to_dict(shared_wall),
    "smallest_kitchen": layout_grid_to_dict(smallest_kitchen),
    "easy_layout": layout_grid_to_dict(easy_layout),
    "no_cooperation": layout_grid_to_dict(no_cooperation),
    "vertical_corridors": layout_grid_to_dict(vertical_corridors),
    "horizontal_corridors": layout_grid_to_dict(horizontal_corridors),
    "resource_sharing": layout_grid_to_dict(resource_sharing),
    "basic_kitchen_large": layout_grid_to_dict(basic_kitchen_large),
}

# Combine legacy and generated easy layouts
easy_layouts = {
    **easy_layouts_legacy,
    **easy_generated_layouts,
}

# All layouts
overcooked_layouts = {
    **hard_layouts,
    **medium_layouts,
    **easy_layouts,
}

# Difficulty-based layout collections
difficulty_layouts = {
    "easy": easy_layouts,
    "medium": medium_layouts,
    "hard": hard_layouts,
}


def get_layouts_by_difficulty(difficulty: str = None):
    """
    Get layouts filtered by difficulty level.

    Args:
        difficulty: One of 'easy', 'medium', 'hard', or None for all layouts

    Returns:
        Dictionary of layouts for the specified difficulty level
    """
    if difficulty is None:
        return overcooked_layouts

    difficulty = difficulty.lower()
    if difficulty not in difficulty_layouts:
        available = list(difficulty_layouts.keys())
        raise ValueError(f"Invalid difficulty '{difficulty}'. Available options: {available}")

    return difficulty_layouts[difficulty]
