import json
import os
from collections import defaultdict
from q3maps import *
import sys

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

    min_arena_version = None
    if len(sys.argv) > 1:
        min_arena_version = int(sys.argv[1])

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

        if min_arena_version:
            version = js.get("arena_version", 0)
            if version < min_arena_version:
                continue

        map_name = js["map"]
        board.setdefault(map_name, defaultdict(BattleStats))
        n = len(js["results"])

        for r in js["results"]:
            name = r["punter"]
            bs = board[map_name][name]
            bs.num_games += 1
            bs.rank_score += n - r["rank"] + 1
            bs.game_score += r["score"]

    penalty = defaultdict(int)
    nMaps = defaultdict(int)

    for m, s in ORIGINAL_MAPS:
        print ''
        print 'Map: {}'.format(m)
        if m in board:
            dd = board[m]

            ll = dd.items()
            ll.sort(key=lambda x : x[1].get_avg_rank_score(), reverse=True)

            iPlayer = 0
            for player, bs in ll:
                if player == "chaos monkey": continue
                print '>>   {} --> {:.3f} avg rank score, {:.2f} score ({} games)'.format(
                    player,
                    bs.get_avg_rank_score(),
                    bs.get_avg_game_score(),
                    bs.num_games)
                penalty[player] += iPlayer
                iPlayer += 1
                nMaps[player] += 1

    ll = list(penalty.iteritems())
    ll.sort(key=lambda x : x[1])
    print("OVERALL")
    for player, penalty in ll:
        if nMaps[player] == len(ORIGINAL_MAPS):
            print("{} --> {}".format(player, penalty))


if __name__ == "__main__":
    run()
