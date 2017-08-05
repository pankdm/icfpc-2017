from collections import defaultdict, deque
from copy import deepcopy
import random

from pprint import pprint
from timeit import default_timer as timer

from graph_util import *

def compute_score(graph, mines, distances):
    total_score = 0
    for mine in mines:
        scores = run_bfs(mine, graph)
        for target in scores:
            d = distances.get(target, {}).get(mine, 0)
            total_score += d * d
    return total_score



class GreedyPunter:
    def __init__(self, config):
        self.name = "greedy monkey"
        self.num_moves = 0
        self.config = config

    def get_handshake(self):
        return {"me": self.name}


    def process_setup(self, data):
        print("Processing setup:")
        pprint(data)

        self.punter_id = data["punter"]
        self.num_punters = data["punters"]

        map_data = data["map"]
        self.graph = defaultdict(set)
        for river in map_data["rivers"]:
            s = river["source"]
            t = river["target"]

            # assume no multiedges for now
            assert t not in self.graph[s]
            assert s not in self.graph[t]

            self.graph[s].add(t)
            self.graph[t].add(s)
        self.graph_readonly = deepcopy(self.graph)

        self.mines = set()
        for mine in map_data["mines"]:
            self.mines.add(mine)

        # compute the scores to each city
        # map : city -> mine -> score
        self.distances = defaultdict(dict)
        for mine in self.mines:
            scores = run_bfs(mine, self.graph)
            for city, score in scores.items():
                self.distances[city][mine] = score

        print('Calculated distances')
        for city, scores in sorted(self.distances.items()):
            print('{} -> {}'.format(city, scores))

        # maintain graph of our nodes
        self.my_graph = defaultdict(set)

        # default reply
        reply = {"ready": self.punter_id}

        # futures = data.get("settings", {}).get("futures", False)
        # if futures:
        #     s, t = self._select_random_future(self.graph)
        #     print 'Selected future: {}'.format((s, t))
        #     reply["futures"] = {
        #         "source": s,
        #         "target": t
        #     }
        return reply

    def process_stop(self, data):
        print('GAME OVER!')
        scores = {}
        result = []
        for score_data in data["scores"]:
            punter_id = score_data["punter"]
            score = score_data["score"]
            scores[punter_id] = score
            result.append( (score, punter_id) )

        result.sort(reverse=True)
        place = 1
        for score, punter_id in result:
            you = ''
            if punter_id == self.punter_id:
                you = '(you)'
            print('{} --> punter {} {} with {} score'.format(
                place, punter_id, you, score))
            place += 1

        # None indicates the game is over
        return None

    def _select_random_edge(self, graph):
        all_edges = []
        for s, nodes in self.graph.items():
            for t in nodes:
                all_edges.append( (s, t) )
        index = random.randint(0, len(all_edges) - 1)
        s, t = all_edges[index]
        return (s, t)

    def _select_random_future(self, graph):
        all_edges = []
        for s, nodes in self.graph.items():
            # skip non-mine sources
            if s not in self.mines:
                continue
            for t in nodes:
                all_edges.append( (s, t) )
        index = random.randint(0, len(all_edges) - 1)
        s, t = all_edges[index]
        return (s, t)

    def _select_greedy_edge(self):
        all_edges = []
        for s, nodes in self.graph.items():
            for t in nodes:
                all_edges.append( (s, t) )

        best_score = None
        best_st = None
        for st in all_edges:
            my_graph_copy = deepcopy(self.my_graph)
            add_edge(my_graph_copy, st)
            score = compute_score(my_graph_copy, self.mines, self.distances)
            if best_score is None or score > best_score:
                best_score = score
                best_st = st

        print('Found {} that would give score {}'.format(st, best_score))
        return st


    def process_move(self, data):
        print ''
        print("Processing move:")
        pprint(data)


        self.num_moves += 1
        # check if this is stop message:
        if "stop" in data:
            return self.process_stop(data["stop"])

        # update the available edges
        if "move" in data:
            for move in data["move"]["moves"]:
                if "claim" in move:
                    s = move["claim"]["source"]
                    t = move["claim"]["target"]
                    st = (s,t)
                    remove_edge(self.graph, st)

                    punter_id = move["claim"]["punter"]
                    if punter_id == self.punter_id:
                        add_edge(self.my_graph, st)

        # take one at random
        # s, t = self._select_random_edge(self.graph)
        # print 'Move: {}, got random move {}'.format(self.num_moves, (s,t))

        start = timer()
        s, t =  self._select_greedy_edge()
        end = timer()
        print ('Finished select_greey_edge in {}s'.format(end - start))

        # add_edge(self.my_graph, (s, t))

        return {
            "claim": {
                "punter": self.punter_id,
                "source": s,
                "target": t,
            },
        }
