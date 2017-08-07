from collections import defaultdict, deque
from copy import deepcopy
import random
import time
import math

from pprint import pprint
from timeit import default_timer as timer

from graph_util import *
from union_find_scores import *
from client import *
import graph_util
import cPickle

class FastGreedyStochasticPunter:
    def __init__(self, config):
        self.name = "fast greedy stochastic monkey" if not config.name else config.name
        self.num_moves = 0
        self.config = config

    def save(self):
        begin = time.clock()
        sData = cPickle.dumps( (self.components, self.world) )
        print("time", time.clock() - begin, "len", len(sData))

    def weight_score(self):
        return 1.0


    def weight_stochastic(self):
        return 0.3


    def weight_bridges(self):
        return 0.0


    def weight_vertices(self):
        return 0.0
    
    
    def get_handshake(self):
        return {"me": self.name}


    def process_setup(self, data):
        if self.config.log:
            print("Processing setup:")
            pprint(data)

        self.punter_id = data["punter"]
        self.num_punters = data["punters"]

        map_data = data["map"]
        self.world = graph_util.World(map_data)

        self.distances = graph_util.compute_distances(self.world)
        all_distances = graph_util.compute_all_distances(self.world)
        t0 = time.clock()
        bridge_scores = graph_util.compute_bridge_scores(self.world, all_distances)
        vertex_scores = graph_util.compute_vertices_centralness(self.world, all_distances)
        for m in self.world.mines:
            vertex_scores[m] += 1.0

        if self.config.log:
            print("vertex_scores", self.vertex_scores)
            print("compute_bridge_scores = %f" % (time.clock() - t0))
            for e, v in self.bridge_scores.iteritems():
                print("bridge score for %s=%f" % (str(e), v))

        if self.config.log:
            print('Calculated distances')
            for city, scores in sorted(self.distances.items()):
                print('{} -> {}'.format(city, scores))

        self.components = ComponentsListWithScores(self.world.vertices, self.world.mines, self.distances, bridge_scores, vertex_scores)
        self.components.start_transaction()
        for v in self.world.vertices:
            for x in self.world.graph[v]:
                self.components.add_edge(v, x)

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
        for s, nodes in self.world.graph.items():
            for t in nodes:
                all_edges.append( (s, t) )
        index = random.randint(0, len(all_edges) - 1)
        s, t = all_edges[index]
        return (s, t)


    def _aggregate_random_scores(self, scores):
        if len(scores) == 0:
            return 0
        return float(max(scores))//2


    def _select_greedy_edge(self):
        all_edges = []
        for s, nodes in self.world.graph.items():
            for t in nodes:
                all_edges.append( (s, t) )
        random.shuffle(all_edges)

        best_score = None
        best_st = None
        current_score = self.components.score()
        current_bridge_score = self.components.bridge_score()
        current_vertex_score = self.components.vertex_score()
        max_score_random_gain = 0
        n_stochastic_steps = 0
        begin0 = time.clock()
        n_processed = 0
        best_score_gain = 0
        best_bridge_gain = 0
        best_vertex_gain = 0
        best_stochastic_gain = 0
        for st in all_edges:
            if time.clock() > begin0 + 0.95:
                break
            n_processed += 1
            s, t = st
            if self.components.component(s) != self.components.component(t):
                self.components.start_transaction()
                self.components.union(s, t)

                score_before_random = self.components.score()
                score_random_gains = []
                n_iterations = 0
                n_stochastic_edges = min(self.components.num_edges() / self.num_punters, 10)
                begin = time.clock()
                c_move_time_limit = 0.7
                score_gain = self.components.score() - current_score
                bridge_score_gain = self.components.bridge_score() - current_bridge_score
                vertex_score_gain = self.components.vertex_score() - current_vertex_score
                while (time.clock() - begin)*len(all_edges) < c_move_time_limit:
                    n_transactions = 0
                    j = 0
                    while j < n_stochastic_edges:
                        if (time.clock() - begin)*len(all_edges) > c_move_time_limit:
                            break
                        if 0 != self.components.num_edges():
                            random_edge = self.components.random_edge()
                            # print random_edge, self.components.component(random_edge[0]), self.components.component(random_edge[1])
                            if self.components.component(random_edge[0]) != self.components.component(random_edge[1]):
                                self.components.start_transaction()
                                self.components.union(random_edge[0], random_edge[1])
                                n_transactions += 1
                                n_stochastic_steps += 1
                                j += 1
                    n_iterations += 1
                    score_random_gains.append(self.components.score() - score_before_random)
                    for j in xrange(n_transactions):
                        self.components.rollback_transaction()

                if score_random_gains:
                    max_score_random_gain = max(max_score_random_gain, score_random_gains[-1])
                stochastic_gain = self._aggregate_random_scores(score_random_gains)
                score = self.weight_score()*score_gain + self.weight_stochastic()*stochastic_gain + self.weight_bridges()*bridge_score_gain + self.weight_vertices()*vertex_score_gain
                # if self.config.log:
                #     print("%f %f %f" % (self.components.score() - current_score, self._aggregate_random_scores(score_random_gains), bridge_score_gain))

                if best_score is None or score > best_score:
                    best_score = score
                    best_st = st
                    best_score_gain = score_gain
                    best_bridge_gain = bridge_score_gain
                    best_vertex_gain = vertex_score_gain
                    best_stochastic_gain = stochastic_gain
                self.components.rollback_transaction()
        if self.config.log:
             print(max_score_random_gain, self.components.num_edges(), n_stochastic_steps, float(n_processed)/len(all_edges), "best_score_gain", best_score_gain, "best_bridge_gain", best_bridge_gain, "best_vertex_gain", best_vertex_gain, "best_stochastic_gain", best_stochastic_gain)

        if self.config.log and best_score:
            print('Found {} that would give score {}'.format(best_st, best_score))

        if best_score is None:
            # choose random if nothing found
            index = random.randint(0, len(all_edges) - 1)
            st = all_edges[index]
            return st

        # raw_input("press enter")

        return best_st


    def process_move(self, data):
        if self.config.log:
            print('')
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
                    remove_edge(self.world.graph, st)

                    punter_id = move["claim"]["punter"]
                    if punter_id == self.punter_id:
                        self.components.union(s, t)
                    else:
                        self.components.remove_edge(s, t)

        # take one at random
        if False and self.num_moves == 1:
            s, t = self._select_random_edge(self.world.graph)
            if self.config.log:
                print('Move: {}, got random move {}'.format(self.num_moves, (s, t)))
        else:
            start = timer()
            s, t =  self._select_greedy_edge()
            end = timer()
            if self.config.log:
                print('Finished select_greedy_edge in {}s'.format(end - start))

        # self.save()

        return {
            "claim": {
                "punter": self.punter_id,
                "source": s,
                "target": t,
            },
        }


class FastGreedyStochasticMaxPunter(FastGreedyStochasticPunter):
    def _aggregate_random_scores(self, scores):
        if len(scores) == 0: 
            return 0
        return float(sum(scores))/len(scores)/2


class FastGreedyStochasticBridgesMaxPunter(FastGreedyStochasticMaxPunter):
    def weight_bridges(self):
        if self.num_moves < 3.0*math.sqrt(len(self.world.vertices)):
            return 10.0
        return 1.0


    def weight_stochastic(self):
        if self.num_moves < 3.0*math.sqrt(len(self.world.vertices)):
            return 0.0
        return 1.0



class FastGreedyStochasticBridgesVerticesMaxPunter(FastGreedyStochasticBridgesMaxPunter):
    def weight_vertices(self):
        if self.num_moves < 2:
            return 50.0
        if self.num_moves < math.sqrt(len(self.world.vertices)):
            return 1.0
        return 0.0


    def weight_stochastic(self):
        if self.num_moves < 3.0*math.sqrt(len(self.world.vertices)):
            return 0.0
        return 1.0


class FastGreedyBridgesVerticesMaxPunter(FastGreedyStochasticBridgesMaxPunter):
    def weight_stochastic(self):
        return 0.0


if __name__ == "__main__":
    config = Config()
    config.log = True

    punter = FastGreedyStochasticPunter(config)
    client = Client(LOCALHOST, 9999)
    client.run(punter)
