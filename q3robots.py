from all_solvers import *
from config import *

def create_all_robots():
    return [
        create_punter(ChaosPunter, name="ChaosSolver"),
        create_punter(FastGreedyPunter, name="FastGreedyPunter"),
    ]
