from collections import defaultdict, deque
from copy import deepcopy
import random
import time

from pprint import pprint
from timeit import default_timer as timer

from graph_util import *
from union_find_fast import *
from client import *

class UberFastGreedyStochasticPunter:
    def __init__(self, config):
        self.name = "coding monkey" if not config.name else config.name
        self.num_moves = 0
        self.config = config
        self.num_edges = 0

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
        self.num_edges = len(map_data["rivers"])
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

        self.mines = sorted(map_data["mines"])
        
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

        self.union = UnionFindFast(n, self.mines, self.distances)
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

    
    def _aggregate_random_scores(self, scores):
        return float(sum(scores))/len(scores)/2

    
    def _select_greedy_edge(self):
        all_edges = []
        for s, nodes in self.graph.items():
            for t in nodes:
                all_edges.append( (s, t) )
        random.shuffle(all_edges)

        best_score = None
        best_st = None
        current_score = self.union.score()
        max_score_random_gain = 0
        n_stochastic_steps = 0
        begin0 = time.clock()
        n_processed = 0
        for st in all_edges:
            if time.clock() > begin0 + 0.95:
                break
            n_processed += 1
            s, t = st
            if self.union.root(s) != self.union.root(t):
                curr_edges = all_edges[:]
                curr_edges.remove(st)
                random.shuffle(curr_edges)
                currUnion = deepcopy(self.union)
                currUnion.union(s, t)

                score_before_random = self.union.score()
                score_random_gains = []
                n_iterations = 0
                stochastic_edges = min(len(curr_edges) / self.num_punters, 10)
                begin = time.clock()
                c_move_time_limit = 0.7
                while (time.clock() - begin)*len(all_edges) < c_move_time_limit:
                    nextUnion = deepcopy(currUnion)
                    n_transactions = 0
                    j = 0
                    while j < stochastic_edges:
                        if (time.clock() - begin)*len(all_edges) > c_move_time_limit:
                            break
                        if 0 != len(curr_edges):
                            random_edge = curr_edges.pop()
                            # print random_edge, self.components.component(random_edge[0]), self.components.component(random_edge[1])
                            if currUnion.root(random_edge[0]) != currUnion.root(random_edge[1]):
                                nextUnion.union(random_edge[0], random_edge[1])
                                n_transactions += 1
                                n_stochastic_steps += 1
                                j += 1
                    n_iterations += 1
                    score_random_gains.append(nextUnion.score() - score_before_random)
    
                max_score_random_gain = max(max_score_random_gain, score_random_gains[-1])
                score = currUnion.score() + self._aggregate_random_scores(score_random_gains)

                if best_score is None or score > best_score:
                    best_score = score
                    best_st = st
                    
        if self.config.log:
            print(max_score_random_gain, self.num_edges, n_stochastic_steps, float(n_processed)/len(all_edges))

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
                    self.num_edges -= 1

                    punter_id = move["claim"]["punter"]
                    if punter_id == self.punter_id:
                        add_edge(self.my_graph, st)
                        self.union.union(s, t)

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
                print ('Finished select_greedy_edge in {}s'.format(end - start))

        return {
            "claim": {
                "punter": self.punter_id,
                "source": s,
                "target": t,
            },
        }

class UberFastGreedyStochasticMaxPunter(UberFastGreedyStochasticPunter):
    def _aggregate_random_scores(self, scores):
        return float(max(scores))//2

if __name__ == "__main__":
    config = Config()
    config.log = True

    punter = UberFastGreedyStochasticPunter(config)
    client = Client(LOCALHOST, 9999)
    client.run(punter)
