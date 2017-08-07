from server import Server

from all_solvers import *


from config import create_punter, Config


import sys
import random

if __name__ == "__main__":
    map_file = sys.argv[1]

    punters = [
        create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 1"),
        create_punter(FastGreedyOptions, log=False, name="FastGreedyPunter 2", use_options=True),

        # create_punter(VladSolver2, name="Vlad-MCTS-2h", timeout=0.9, search_width=15, magic_moves=True, greedy_threshold=50),
        # create_punter(FastGreedyStochasticBridgesVerticesMaxPunter, name="FastGreedyStochasticBridgesVerticesMaxPunter"),


        # create_punter(ChaosOptionsPunter, log=True, name="ChaosPunter 1"),
        # create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 2"),
        # create_punter(ChaosPunter, log=False, name="ChaosPunter 2"),
        # create_punter(ChaosPunter, log=False, name="ChaosPunter 3"),
        # create_punter(ChaosPunter, log=False, name="ChaosPunter 4"),
        #  create_punter(GreedyPunter, log=False, name="GreedyPunter 1"),
        # create_punter(GreedyPunter, log=False, name="GreedyPunter 2"),
        # create_punter(GreedyPunter, log=False, name="GreedyPunter 3"),
        # create_punter(GreedyPunter, log=False, name="GreedyPunter 4"),
        # create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 1"),
        # create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 2"),
        # create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 3"),
        # create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 4"),
        # create_punter(VladSolver2, log=False, name="VladSolver2 1"),
        # create_punter(FastGreedyStochasticPunter, log=False, name="FastGreedyStochasticPunter 1"),
        # create_punter(FastGreedyStochasticMaxPunter, log=False, name="FastGreedyStochasticMaxPunter 1"),
        # create_punter(FastGreedyStochasticBridgesMaxPunter, log=True, name="FastGreedyStochasticBridgesMaxPunter 1"),
    ]
    # random.shuffle(punters)

    settings = {
        "futures": True,
        "splurges": True,
        "options": True,
    }

    config = Config()
    config.log = True

    s = Server(punters, map_file, settings, config)
    s.run()
