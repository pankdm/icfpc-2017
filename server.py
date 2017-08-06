import json

from pprint import pprint
from copy import deepcopy
from collections import defaultdict

from graph_util import (
    add_edge,
    compute_distances,
    run_bfs,
    World,
)

from config import Config


class FinalScore:
    def __init__(self):
        self.rank = 0
        self.score = 0

def update_punter_id(move, punter_id):
    move.get("claim", {})["punter"] = punter_id


def canonical(s, t):
    if s < t: return (s, t)
    return (t, s)

def compute_score(graph, mines, distances, future_st):
    total_score = 0
    for mine in mines:
        scores = run_bfs(mine, graph)
        for target in scores:
            d = distances.get(target, {}).get(mine, 0)
            total_score += d * d

        if future_st is not None:
            s, t = future_st
            if s == mine:
                d = distances.get(t, {}).get(mine, 0)
                if t in scores:
                    total_score += d ** 3
                else:
                    total_score -= d ** 3

    return total_score


class Server:
    def __init__(self, punters, map_file, settings, config=Config()):
        self.config = config

        self.punters = punters
        self.js_map = json.loads(open(map_file, 'rt').read())
        self.settings = settings
        # pprint(self.js_map)

        self.world = World(self.js_map)
        self.distances = compute_distances(self.world)

        if self.config.log:
            print('Calculated distances')
            for city, scores in sorted(self.distances.items()):
                print('{} -> {}'.format(city, scores))

        self.total_moves = len(self.js_map["rivers"])
        # debugging
        # self.total_moves = 1

        # map from punter_id to move.
        # we keep only latest
        self.previous_moves = {}

        # current state of roads claimed by punters
        self.per_punter_graph = {}
        for i in range(len(self.punters)):
            self.per_punter_graph[i] = defaultdict(set)

        # map from canonical presentation to punter_id
        self.claimed_roads = {}

        # map punter_id -> future (s, t)
        self.futures = {}
        self.futures_enabled = settings.get("futures", False)

    def _apply_move(self, move, punter_id):
        if "claim" not in move:
            return

        s = move["claim"]["source"]
        t = move["claim"]["target"]
        st = canonical(s, t)
        if st not in self.claimed_roads:
            self.claimed_roads[st] = punter_id
            add_edge(self.per_punter_graph[punter_id], st)


    def _compute_scores(self):
        result = []
        for punter_id, graph in self.per_punter_graph.items():
            future_st = self.futures.get(punter_id, None)
            score = compute_score(
                graph, self.world.mines, self.distances, future_st)
            data = {
                "punter": punter_id,
                "score": score,
            }
            result.append(data)
        return result

    def run(self):
        n = len(self.punters)
        punter_id2name = {}
        for p_index, p in enumerate(self.punters):
            data = {
                "punter": p_index,
                "punters": n,
                "map": deepcopy(self.js_map),
                "settings": self.settings,
            }
            punter_id2name[p_index] = p.get_handshake()["me"]
            # Ignore reply for now
            reply = p.process_setup(data)
            futures = reply.get("futures", [])
            if self.futures_enabled and futures:
                f = futures[-1]
                s = f["source"]
                t = f["target"]
                self.futures[p_index] = (s, t)

        num_moves = 0
        while num_moves < self.total_moves:
            for p_index, p in enumerate(self.punters):
                if self.config.log:
                    print
                    print '{}/{} == next round =='.format(num_moves + 1, self.total_moves)
                moves = []
                for punter_id, move in self.previous_moves.items():
                    moves.append(move)

                data = {
                    "move": {
                        "moves" : moves,
                    },
                }
                next_move = p.process_move(data)
                update_punter_id(next_move, p_index)
                self.previous_moves[p_index] = next_move

                self._apply_move(next_move, p_index)

                num_moves += 1
                if num_moves >= self.total_moves:
                    # we did all moves
                    break

        # now count scores and send this information to punters
        scores = self._compute_scores()
        data = {
            "stop" : {
                "moves" : [],
                "scores": scores,
            }
        }
        for p in self.punters:
            p.process_move(data)

        if self.config.log:
            print('GAME OVER ON SERVER!')
        result = []
        for score_data in scores:
            punter_id = score_data["punter"]
            score = score_data["score"]
            result.append( (score, punter_id) )

        # could be used to obtain results from outside
        self.final_score = {}

        self.results_to_log = []

        result.sort(reverse=True)
        place = 1
        for score, punter_id in result:
            if self.config.log:
                print('{} --> punter \'{}\' with {} score'.format(
                    place, punter_id2name[punter_id], score))

            final_score = FinalScore()
            final_score.score = score
            final_score.rank = place
            self.final_score[punter_id2name[punter_id]] = final_score

            self.results_to_log.append({
                "punter": punter_id2name[punter_id],
                "score": score,
                "rank": place,
            })

            place += 1
