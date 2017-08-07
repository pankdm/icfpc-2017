from all_solvers import *
from config import *

# def create_all_robots():
#     return [
#         create_punter(ChaosPunter, name="ChaosSolver"),
#         create_punter(FastGreedyPunter, name="FastGreedyPunter"),
#         create_punter(FastGreedyStochasticPunter, name="FastGreedyStochasticPunter"),
#         create_punter(FastGreedyStochasticBridgesMaxPunter, name="FastGreedyStochasticBridgesMaxPunter"),
#         create_punter(VladSolver2, name="Vlad-MCTS-2j"),
#         create_punter(VladSolver3, name="Vlad-MG-3b", timeout=0.8),
#         create_punter(VladSolver4, name="Vlad-MG-4b", timeout=0.8),
#         create_punter(FastGreedyStochasticBridgesVerticesMaxPunter, name="FastGreedyStochasticBridgesVerticesMaxPunter"),
#         create_punter(FastGreedyBridgesVerticesMaxPunter, name="FastGreedyBridgesVerticesMaxPunter"),
#         # create_punter(UberFastGreedyStochasticPunter, name="UberFastGreedyStochasticPunter"),
#     ]

def create_all_robots():
    return [
        create_punter(ChaosPunter, name="ChaosSolver"),
        create_punter(VladSolver2, name="Vlad-MCTS-2j", timeout=0.8),
        create_punter(FastGreedyPunter, name="FastGreedyPunter"),
        create_punter(FastGreedyPunter, name="FastSplurges", splurges_on_claim=True),
        create_punter(FastGreedyOptions, name="Fast Options", use_options=True),
        create_punter(MetaPunter, name="Meta"),
        create_punter(FastGreedyOptions, name="dummy Fast Options", use_options=False),
    ]


# please increment when you add new robots
ARENA_VERSION = 20
