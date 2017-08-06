import json
import os
from collections import defaultdict
from q3maps import *

class BattleStats:
    def __init__(self):
        self.num_games = 0
        self.rank_score = 0
        self.game_score = 0

    def get_avg_rank_score(self):
        if self.num_games == 0: return 0
        else:
            return self.rank_score * 1.0 / self.num_games

    def get_avg_game_score(self):
        if self.num_games == 0: return 0
        else:
            return self.game_score * 1.0 / self.num_games



def run():
    board = {}

    loc = 'arena/results'
    files = os.listdir(loc)

    it = 0
    counter = int(0.01 * len(files))

    for f in files:
        it += 1
        if it >= counter:
            it = 0
            print 'processing file {}'.format(f)

        js_data = open('{}/{}'.format(loc, f), 'rt').read()
        try:
            js = json.loads(json.loads(js_data))
        except Exception as e:
            print f, 'Error:', e

        map_name = js["map"]
        board.setdefault(map_name, defaultdict(BattleStats))
        n = len(js["results"])

        for r in js["results"]:
            name = r["punter"]
            bs = board[map_name][name]
            bs.num_games += 1
            bs.rank_score += n - r["rank"] + 1
            bs.game_score += r["score"]


    for m, s in ORIGINAL_MAPS:
        print ''
        print 'Map: {}'.format(m)
        if m in board:
            dd = board[m]

            ll = dd.items()
            ll.sort(key=lambda x : x[1].get_avg_rank_score(), reverse=True)

            for player, bs in ll:
                if player == "chaos monkey": continue
                print '>>   {} --> {} rank, {} score ({} games)'.format(
                    player,
                    bs.get_avg_rank_score(),
                    bs.get_avg_game_score(),
                    bs.num_games)

if __name__ == "__main__":
    run()
