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

def run_battle(stats):
    map_file = sys.argv[1]

    if len(sys.argv) > 2:
        seed = int(sys.argv[2])
    else:
        seed = random.randint(0, 1000)
    # print 'Running with seed: {}'.format(seed)
    random.seed(seed)

    punters = [
        #create_punter(ChaosPunter, log=False, name="Chaos1"),
        #create_punter(ChaosPunter, log=False, name="Chaos2"),
        #create_punter(VladSolver1, name="Vlad MCTS", timeout=0.95),
        
        #create_punter(FastGreedyStochasticPunter, name="FastStoch"),
        #create_punter(FastGreedyStochasticMaxPunter, name="FastStochMax"),
        #create_punter(VladSolver1, name="Vlad MCTS", timeout=0.95),
        
        #create_punter(VladSolver1, name="Vlad MCTS", timeout=0.05),

        create_punter(VladSolver1, name="Vlad MCTS SW", timeout=0.45, sum_norm=True, weighted_move=True),
        create_punter(VladSolver1, name="Vlad MCTS S", timeout=0.45, sum_norm=True),
        
        #create_punter(GreedyPunter, log=False, name="Greedy 1"),
        #create_punter(FastGreedyStochasticPunter, name="Fast Stochastic"),
        #create_punter(VladSolver1, name="Vlad MCTS 0.50", timeout=0.50),
        #create_punter(VladSolver1, name="Vlad MCTS 0.50", timeout=0.50),
    ]
    settings = {
        "futures": True
    }

    s = Server(punters, map_file, settings)
    s.run()

    final_score = s.final_score
    stats.update_results(final_score)


if __name__ == "__main__":
    stats = Stats()

    while True:
        run_battle(stats)
        stats.show_results()
