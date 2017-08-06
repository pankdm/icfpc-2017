from collections import defaultdict, deque
from copy import deepcopy
import random

from pprint import pprint
from timeit import default_timer as timer

from graph_util import *
from union_find_scores import *
from client import *

class FastGreedyStochasticPunter:
    def __init__(self, config):
        self.name = "greedy monkey" if not config.name else config.name
        self.num_moves = 0
        self.config = config


    def compute_score_slow(graph, mines, distances):
        total_score = 0
        for mine in mines:
            scores = run_bfs(mine, graph)
            for target in scores:
                d = distances.get(target, {}).get(mine, 0)
                total_score += d * d
        return total_score


    def get_handshake(self):
        return {"me": self.name}


    def process_setup(self, data):
        if self.config.log:
            print("Processing setup:")
            pprint(data)

        self.punter_id = data["punter"]
        self.num_punters = data["punters"]

        map_data = data["map"]
        self.graph = defaultdict(set)
        n = 0
        for river in map_data["rivers"]:
            s = river["source"]
            t = river["target"]

            # assume no multiedges for now
            assert t not in self.graph[s]
            assert s not in self.graph[t]

            self.graph[s].add(t)
            self.graph[t].add(s)

            n = max(n, s)
            n = max(n, t)
        n += 1
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

        if self.config.log:
            print('Calculated distances')
            for city, scores in sorted(self.distances.items()):
                print('{} -> {}'.format(city, scores))

        self.components = ComponentsListWithScores(n, self.mines, self.distances)
        self.components.start_transaction()
        for i in xrange(n):
            for x in self.graph[i]:
                self.components.add_edge(i, x)
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
        if not self.config.log:
            return None

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

    def _select_greedy_edge(self):
        all_edges = []
        for s, nodes in self.graph.items():
            for t in nodes:
                all_edges.append( (s, t) )

        best_score = None
        best_st = None
        current_score = self.components.score()
        for st in all_edges:
            s, t = st
            if self.components.component(s) != self.components.component(t):
                self.components.start_transaction()
                self.components.union(s, t)

                score_before_random = self.components.score()
                score_random_gain = 0
                n_iterations = 0
                stochastic_edges = min(self.components.num_edges() / self.num_punters, 10)
                for i in xrange(10):
                    n_transactions = 0
                    for j in xrange(stochastic_edges):
                        if 0 != self.components.num_edges():
                            random_edge = self.components.random_edge()
                            # print random_edge, self.components.component(random_edge[0]), self.components.component(random_edge[1])
                            if self.components.component(random_edge[0]) != self.components.component(random_edge[1]):
                                self.components.start_transaction()
                                self.components.union(random_edge[0], random_edge[1])
                                n_transactions += 1
                    n_iterations += 1
                    score_random_gain += self.components.score() - score_before_random
                    for j in xrange(n_transactions):
                        self.components.rollback_transaction()
    
                if 0 != n_iterations:
                    score_random_gain = float(score_random_gain)/n_iterations

                score = self.components.score() + score_random_gain

                if best_score is None or score > best_score:
                    best_score = score
                    best_st = st
                self.components.rollback_transaction()

        if self.config.log:
            print('Found {} that would give score {}'.format(best_st, best_score - current_score))

        if best_score is None:
            # choose random if nothing found
            index = random.randint(0, len(all_edges) - 1)
            st = all_edges[index]
            return st

        # raw_input("press enter")

        return best_st


    def process_move(self, data):
        if self.config.log:
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
                    st = (s, t)
                    remove_edge(self.graph, st)

                    punter_id = move["claim"]["punter"]
                    if punter_id == self.punter_id:
                        add_edge(self.my_graph, st)

                        self.components.union(s, t)
                    else:
                        self.components.remove_edge(s, t)

        # take one at random
        if False and self.num_moves == 1:
            s, t = self._select_random_edge(self.graph)
            if self.config.log:
                print 'Move: {}, got random move {}'.format(self.num_moves, (s, t))
        else:
            start = timer()
            s, t =  self._select_greedy_edge()
            end = timer()
            if self.config.log:
                print ('Finished select_greey_edge in {}s'.format(end - start))

        return {
            "claim": {
                "punter": self.punter_id,
                "source": s,
                "target": t,
            },
        }

if __name__ == "__main__":
    config = Config()
    config.log = True

    punter = FastGreedyStochasticPunter(config)
    client = Client(LOCALHOST, 9999)
    client.run(punter)
