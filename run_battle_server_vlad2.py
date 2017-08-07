from server import Server

from config import create_punter

from all_solvers import *
from includes import *

import random
import sys

class Stats:
    def __init__(self):
        self.total_score = defaultdict(int)
        self.total_rank = defaultdict(int)
        self.num_rounds = 0

    def update_results(self, final_score):
        self.num_rounds += 1
        for punter, final_score in final_score.items():
            self.total_score[punter] += final_score.score
            self.total_rank[punter] += final_score.rank

    def show_results(self):
        output = ''
        for punter in sorted(self.total_score):
            avg = self.total_score[punter] * 1.0 / self.num_rounds
            avg_rank = self.total_rank[punter] * 1.0 / self.num_rounds
            output += ' | {}: {:.2f} ({:.2f} rank)'.format(punter, avg, avg_rank)
        print 'Round {} ### {}'.format(self.num_rounds, output)

def run_battle(stats, it):
    map_file = sys.argv[1]

    if len(sys.argv) > 2:
        seed = int(sys.argv[2])
    else:
        seed = random.randint(0, 1000)
    random.seed(seed)

    punters = [
        #create_punter(GreedyPunter, log=False, name="Greedy 1"),
        #create_punter(ChaosPunter, log=False, name="Chaos1"),

        #create_punter(FastGreedyStochasticPunter, name="FastStoch"),
        #create_punter(FastGreedyStochasticMaxPunter, name="FastStochMax"),
        #create_punter(VladSolver1, name="Vlad MCTS", timeout=0.95),

        #create_punter(VladSolver1, name="Vlad MCTS max", timeout=0.45, sum_norm=False),
        #create_punter(VladSolver1, name="Vlad MCTS inf", timeout=0.45, sum_norm=True),
        #create_punter(FastGreedyStochasticPunter, name="FastStoch"),

        create_punter(FastGreedyPunter, name="FastGreedy"),
        create_punter(VladSolver3, name="VladMetaGreedy4", timeout=0.9, log=True),

        #create_punter(VladSolver1, name="Vlad MCTS   ", timeout=0.45, log=True),
        #create_punter(VladSolver2, name="Vlad MCTS-2  ", timeout=0.45, search_width=15, magic_moves=True, greedy_threshold=50, log=True),
    ]
    settings = {
        "futures": True
    }

    # rotate punters to have more consistent results
    it = it % len(punters)
    punters = punters[it : ] + punters[ : it]
    # print punters

    s = Server(punters, map_file, settings)
    s.run()

    final_score = s.final_score
    stats.update_results(final_score)


if __name__ == "__main__":
    stats = Stats()

    it = 0
    while True:
        run_battle(stats, it)
        stats.show_results()
        it += 1
