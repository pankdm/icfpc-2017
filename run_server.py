from server import Server

from greedy_punter import GreedyPunter
from chaos_punter import ChaosPunter

from config import create_punter


import sys

if __name__ == "__main__":
    map_file = sys.argv[1]

    punters = [
        create_punter(ChaosPunter, log=False),
        create_punter(GreedyPunter),
    ]

    s = Server(punters, map_file)
    s.run()
