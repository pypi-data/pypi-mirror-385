import numpy as np
from ortools.sat.python import cp_model

from puzzle_solver.core.utils import Pos, get_all_pos, set_char, get_neighbors4, in_bounds, Direction, get_next_pos, get_char
from puzzle_solver.core.utils_ortools import and_constraint, or_constraint, generic_solve_all, SingleSolution


def get_ray(pos: Pos, V: int, H: int, direction: Direction) -> list[Pos]:
    out = []
    while True:
        pos = get_next_pos(pos, direction)
        if not in_bounds(pos, V, H):
            break
        out.append(pos)
    return out


class Board:
    def __init__(self, clues: np.ndarray):
        assert clues.ndim == 2 and clues.shape[0] > 0 and clues.shape[1] > 0, f'clues must be 2d, got {clues.ndim}'
        assert all(isinstance(i.item(), int) and i.item() >= -1 for i in np.nditer(clues)), f'clues must be -1 or >= 0, got {list(np.nditer(clues))}'
        self.V = clues.shape[0]
        self.H = clues.shape[1]
        self.clues = clues
        self.model = cp_model.CpModel()

        # Core vars
        self.b: dict[Pos, cp_model.IntVar] = {}  # 1=black, 0=white
        self.w: dict[Pos, cp_model.IntVar] = {}  # 1=white, 0=black
        # Connectivity helpers
        self.root: dict[Pos, cp_model.IntVar] = {}       # exactly one root; root <= w
        self.reach_layers: list[dict[Pos, cp_model.IntVar]] = []  # R_t[p] booleans, t = 0..T

        self.create_vars()
        self.add_all_constraints()

    def create_vars(self):
        # Cell color vars
        for pos in get_all_pos(self.V, self.H):
            self.b[pos] = self.model.NewBoolVar(f"b[{pos}]")
            self.w[pos] = self.model.NewBoolVar(f"w[{pos}]")
            self.model.AddExactlyOne([self.b[pos], self.w[pos]])

        # Root
        for pos in get_all_pos(self.V, self.H):
            self.root[pos] = self.model.NewBoolVar(f"root[{pos}]")

        # Percolation layers R_t (monotone flood fill)
        T = self.V * self.H  # large enough to cover whole board
        for t in range(T + 1):
            Rt: dict[Pos, cp_model.IntVar] = {}
            for pos in get_all_pos(self.V, self.H):
                Rt[pos] = self.model.NewBoolVar(f"R[{t}][{pos}]")
            self.reach_layers.append(Rt)

    def add_all_constraints(self):
        self.no_adjacent_blacks()
        self.white_connectivity_percolation()
        self.range_clues()

    def no_adjacent_blacks(self):
        cache = set()
        for p in get_all_pos(self.V, self.H):
            for q in get_neighbors4(p, self.V, self.H):
                if (p, q) in cache:
                    continue
                cache.add((p, q))
                self.model.Add(self.b[p] + self.b[q] <= 1)


    def white_connectivity_percolation(self):
        """
        Layered percolation:
          - root is exactly the first white cell
          - R_t is monotone nondecreasing in t (R_t+1 >= R_t)
          - A cell can 'turn on' at layer t+1 iff it's white and has a neighbor on at layer t (or is root)
          - Final layer is equal to the white mask: R_T[p] == w[p]  => all whites are connected to the unique root
        """
        # to find unique solutions easily, we make only 1 possible root allowed; root is exactly the first white cell
        prev_cells_black: list[cp_model.IntVar] = []
        for pos in get_all_pos(self.V, self.H):
            and_constraint(self.model, target=self.root[pos], cs=[self.w[pos]] + prev_cells_black)
            prev_cells_black.append(self.b[pos])

        # Seed: R0 = root
        for pos in get_all_pos(self.V, self.H):
            self.model.Add(self.reach_layers[0][pos] == self.root[pos])

        T = len(self.reach_layers)
        for t in range(1, T):
            Rt_prev = self.reach_layers[t - 1]
            Rt = self.reach_layers[t]
            for p in get_all_pos(self.V, self.H):
                # Rt[p] = Rt_prev[p] | (white[p] & Rt_prev[neighbour #1]) | (white[p] & Rt_prev[neighbour #2]) | ...
                # Create helper (white[p] & Rt_prev[neighbour #X]) for each neighbor q
                neigh_helpers: list[cp_model.IntVar] = []
                for q in get_neighbors4(p, self.V, self.H):
                    a = self.model.NewBoolVar(f"A[{t}][{p}]<-({q})")
                    and_constraint(self.model, target=a, cs=[self.w[p], Rt_prev[q]])
                    neigh_helpers.append(a)
                or_constraint(self.model, target=Rt[p], cs=[Rt_prev[p]] + neigh_helpers)

        # All whites must be reached by the final layer
        RT = self.reach_layers[T - 1]
        for p in get_all_pos(self.V, self.H):
            self.model.Add(RT[p] == self.w[p])

    def range_clues(self):
        # For each numbered cell c with value k:
        #   - Force it white (cannot be black)
        #   - Build visibility chains in four directions (excluding the cell itself)
        #   - Sum of visible whites = 1 (itself) + sum(chains) == k
        for pos in get_all_pos(self.V, self.H):
            k = get_char(self.clues, pos)
            if k == -1:
                continue
            # Numbered cell must be white
            self.model.Add(self.b[pos] == 0)

            # Build visibility chains per direction (exclude self)
            vis_vars: list[cp_model.IntVar] = []
            for direction in Direction:
                ray = get_ray(pos, self.V, self.H, direction)  # cells outward
                if not ray:
                    continue
                # Chain: v0 = w[ray[0]]; vt = w[ray[t]] & vt-1
                prev = None
                for idx, cell in enumerate(ray):
                    v = self.model.NewBoolVar(f"vis[{pos}]->({direction.name})[{idx}]")
                    vis_vars.append(v)
                    if idx == 0:
                        # v0 == w[cell]
                        self.model.Add(v == self.w[cell])
                    else:
                        and_constraint(self.model, target=v, cs=[self.w[cell], prev])
                    prev = v

            # 1 (self) + sum(vis_vars) == k
            self.model.Add(1 + sum(vis_vars) == k)

    def solve_and_print(self, verbose: bool = True):
        def board_to_solution(board: Board, solver: cp_model.CpSolverSolutionCallback) -> SingleSolution:
            assignment: dict[Pos, int] = {}
            for pos, var in board.b.items():
                assignment[pos] = solver.Value(var)
            return SingleSolution(assignment=assignment)
        def callback(single_res: SingleSolution):
            print("Solution:")
            res = np.full((self.V, self.H), ' ', dtype=object)
            for pos in get_all_pos(self.V, self.H):
                c = 'B' if single_res.assignment[pos] == 1 else ' '
                set_char(res, pos, c)
            print(res)
        return generic_solve_all(self, board_to_solution, callback=callback if verbose else None, verbose=verbose)
