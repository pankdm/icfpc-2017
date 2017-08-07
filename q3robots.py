from all_solvers import *
from config import *

def create_all_robots():
    return [
        create_punter(ChaosPunter, name="ChaosSolver"),
        create_punter(FastGreedyPunter, name="FastGreedyPunter"),
        create_punter(FastGreedyStochasticPunter, name="FastGreedyStochasticPunter"),
        create_punter(FastGreedyStochasticBridgesMaxPunter, name="FastGreedyStochasticBridgesMaxPunter"),
        create_punter(VladSolver2, name="Vlad-MCTS-2i", timeout=0.8, search_width=15, magic_moves=True, greedy_threshold=9999, playout_max_depth=50),
        create_punter(VladSolver3, name="Vlad-MG-3", timeout=0.8),
        create_punter(VladSolver4, name="Vlad-MG-4", timeout=0.8),
        create_punter(FastGreedyStochasticBridgesVerticesMaxPunter, name="FastGreedyStochasticBridgesVerticesMaxPunter"),
        # create_punter(UberFastGreedyStochasticPunter, name="UberFastGreedyStochasticPunter"),
    ]

# please increment when you add new robots
ARENA_VERSION = 12
