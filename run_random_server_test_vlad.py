from server import Server

from greedy_punter import GreedyPunter
from chaos_punter import ChaosPunter
from vlad_solver1 import VladSolver1

from config import create_punter


import sys

if __name__ == "__main__":
    map_file = sys.argv[1]

    punters = [
        create_punter(ChaosPunter, log=False, name="ChaosPunter 1"),
        create_punter(GreedyPunter, log=False, name="Greedy 1"),
        #create_punter(VladSolver1, name="Vlad MCTS 1"),

        #create_punter(GreedyPunter, log=False, name="Greedy 1"),
        #create_punter(VladSolver1, name="Vlad MCTS 1b", timeout=2.0),
    ]
    settings = {
        "futures": False
    }

    s = Server(punters, map_file, settings)
    s.run()
