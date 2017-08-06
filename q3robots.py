from all_solvers import *
from config import *

def create_all_robots():
    return [
        create_punter(ChaosPunter, name="ChaosSolver"),
        create_punter(FastGreedyPunter, name="FastGreedyPunter"),
        create_punter(FastGreedyStochasticPunter, name="FastGreedyStochasticPunter"),
        create_punter(VladSolver1, name="Vlad-MCTS-rnd-sum", sum_norm=True, rand_edges=True),
    ]
