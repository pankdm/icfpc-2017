from server import Server

from fast_greedy_punter import FastGreedyPunter
from greedy_punter import GreedyPunter
from chaos_punter import ChaosPunter

from config import create_punter

import random
import sys


def run_battle():
    map_file = sys.argv[1]

    if len(sys.argv) > 2:
        seed = int(sys.argv[2])
    else:
        seed = random.randint(0, 1000)
    print 'Running with seed: {}'.format(seed)
    random.seed(seed)

    punters = [
        create_punter(ChaosPunter, log=False, name="ChaosPunter 1"),
        # create_punter(ChaosPunter, log=False, name="ChaosPunter 2"),
        # create_punter(ChaosPunter, log=False, name="ChaosPunter 3"),
        # create_punter(ChaosPunter, log=False, name="ChaosPunter 4"),
        # create_punter(GreedyPunter, log=False, name="GreedyPunter 1"),
        # create_punter(GreedyPunter, log=False, name="GreedyPunter 2"),
        # create_punter(GreedyPunter, log=False, name="GreedyPunter 3"),
        # create_punter(GreedyPunter, log=False, name="GreedyPunter 4"),
        # create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 1"),
        # create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 2"),
        # create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 3"),
        create_punter(FastGreedyPunter, log=False, name="FastGreedyPunter 4"),
    ]
    settings = {
        "futures": True
    }

    s = Server(punters, map_file, settings)
    s.run()


if __name__ == "__main__":
    while True:
        run_battle()
