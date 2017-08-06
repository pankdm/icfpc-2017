from all_solvers import *
from config import *

def create_all_robots():
    return [
        create_punter(ChaosPunter, name="ChaosSolver"),
        create_punter(FastGreedyPunter, name="FastGreedyPunter"),
        create_punter(FastGreedyStochasticPunter, name="FastGreedyStochasticPunter"),
        create_punter(VladSolver1, name="Vlad-MCTS-15", timeout=0.9, search_width=15),
        create_punter(VladSolver1, name="Vlad-MCTS-15m", timeout=0.9, search_width=15, magic_moves=True),
    ]
