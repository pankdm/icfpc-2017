from server import Server

from fast_greedy_punter import FastGreedyPunter
from greedy_punter import GreedyPunter
from greedy_punter2 import GreedyPunter2
from chaos_punter import ChaosPunter

from config import create_punter, Config


import sys

if __name__ == "__main__":
    map_file = sys.argv[1]

    punters = [
        # create_punter(ChaosPunter, log=False, name="ChaosPunter 1"),
        # create_punter(ChaosPunter, log=False, name="ChaosPunter 2"),
        # create_punter(ChaosPunter, log=False, name="ChaosPunter 3"),
        create_punter(ChaosPunter, log=False, name="ChaosPunter 4"),
        # create_punter(GreedyPunter, log=False, name="GreedyPunter 1"),
        # create_punter(GreedyPunter, log=False, name="GreedyPunter 2"),
        # create_punter(GreedyPunter, log=False, name="GreedyPunter 3"),
        # create_punter(GreedyPunter, log=False, name="GreedyPunter 4"),
        create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 1"),
        create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 2"),
        create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 3"),
        create_punter(FastGreedyPunter, log=True, name="FastGreedyPunter 4"),
    ]
    settings = {
        "futures": True,
    }

    config = Config()
    config.log = True

    s = Server(punters, map_file, settings, config)
    s.run()
