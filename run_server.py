from server import Server

from greedy_punter import GreedyPunter
from chaos_punter import ChaosPunter

from config import create_punter


import sys

if __name__ == "__main__":
    map_file = sys.argv[1]

    punters = [
        # create_punter(ChaosPunter, log=False, name="ChaosPunter 1"),
        # create_punter(ChaosPunter, log=False, name="ChaosPunter 2"),
        # create_punter(ChaosPunter, log=False, name="ChaosPunter 3"),
        # create_punter(ChaosPunter, log=False, name="ChaosPunter 4"),
        create_punter(GreedyPunter, log=False, name="GreedyPunter 1"),
        create_punter(GreedyPunter, log=False, name="GreedyPunter 2"),
        create_punter(GreedyPunter, log=False, name="GreedyPunter 3"),
        create_punter(GreedyPunter, log=False, name="GreedyPunter 4"),
    ]
    settings = {
        "futures": True
    }

    s = Server(punters, map_file, settings)
    s.run()
