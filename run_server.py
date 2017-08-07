from server import Server

from fast_greedy_punter import FastGreedyPunter
from fast_greedy_stochastic_punter import FastGreedyStochasticPunter, FastGreedyStochasticMaxPunter, FastGreedyStochasticBridgesMaxPunter, FastGreedyStochasticBridgesVerticesMaxPunter
from vlad_solver2 import VladSolver2
from greedy_punter import GreedyPunter
from greedy_punter2 import GreedyPunter2
from chaos_punter import ChaosPunter

from config import create_punter, Config


import sys
import random

if __name__ == "__main__":
    map_file = sys.argv[1]

    punters = [
        create_punter(ChaosPunter, log=False, name="ChaosPunter 1"),
        create_punter(ChaosPunter, log=False, name="ChaosPunter 2"),
        create_punter(ChaosPunter, log=False, name="ChaosPunter 3"),
        create_punter(ChaosPunter, log=False, name="ChaosPunter 4"),
         create_punter(GreedyPunter, log=False, name="GreedyPunter 1"),
        # create_punter(GreedyPunter, log=False, name="GreedyPunter 2"),
        # create_punter(GreedyPunter, log=False, name="GreedyPunter 3"),
        # create_punter(GreedyPunter, log=False, name="GreedyPunter 4"),
        # create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 1"),
        # create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 2"),
        create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 3"),
        create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 4"),
        create_punter(VladSolver2, log=False, name="VladSolver2 1"),
        create_punter(FastGreedyStochasticPunter, log=False, name="FastGreedyStochasticPunter 1"),
        create_punter(FastGreedyStochasticMaxPunter, log=False, name="FastGreedyStochasticMaxPunter 1"),
        create_punter(FastGreedyStochasticBridgesMaxPunter, log=False, name="FastGreedyStochasticBridgesMaxPunter 1"),
        create_punter(FastGreedyStochasticBridgesVerticesMaxPunter, log=False, name="FastGreedyStochasticBridgesVerticesMaxPunter 1"),
    ]
    random.shuffle(punters)

    settings = {
        "futures": True,
    }

    config = Config()
    config.log = True

    s = Server(punters, map_file, settings, config)
    s.run()
