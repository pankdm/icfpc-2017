from collections import defaultdict, deque
from copy import deepcopy
import random

from pprint import pprint
from timeit import default_timer as timer

from graph_util import *
from union_find_scores import *
from client import *
import graph_util

def compute_score_slow(graph, mines, distances):
    total_score = 0
    for mine in mines:
        scores = run_bfs(mine, graph)
        for target in scores:
            d = distances.get(target, {}).get(mine, 0)
            total_score += d * d
    return total_score


class FastGreedyOptions:
    def __init__(self, config):
        self.name = "greedy monkey" if not config.name else config.name
        self.num_moves = 0
        self.config = config

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
        self.graph = self.world.graph
        self.graph_readonly = deepcopy(self.graph)

        self.mines = self.world.mines

        self.distances = graph_util.compute_distances(self.world)

        if self.config.log:
            print('Calculated distances')
            for city, scores in sorted(self.distances.items()):
                print('{} -> {}'.format(city, scores))

        self.components = ComponentsListWithScores(self.world.n, self.mines, self.distances)
        for i in xrange(self.world.n):
            for x in self.graph[i]:
                self.components.add_edge(i, x)
        # maintain graph of our nodes
        self.my_graph = defaultdict(set)

        # credit of moves
        self.my_credit = 0

        # credit of options
        self.my_options = len(self.world.mines)
        self.available_for_option = set()


        # default reply
        reply = {"ready": self.punter_id}

        self.settings = data.get("settings", {})

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

        random.shuffle(all_edges)

        best_score = None
        best_st = None
        best_type = "claim"
        current_score = self.components.score()
        for st in all_edges:
            s, t = st
            if self.components.component(s) != self.components.component(t):
                self.components.start_transaction()
                self.components.union(s, t)
                score = self.components.score()
                if best_score is None or score > best_score:
                    best_score = score
                    best_st = st
                self.components.rollback_transaction()

        if self.my_options > 0:
            for st in self.available_for_option:
                s, t = st
                if self.components.component(s) != self.components.component(t):
                    self.components.start_transaction()
                    self.components.union(s, t)
                    score = self.components.score()
                    if best_score is None or score > best_score + 5:
                        best_score = score
                        best_st = st
                        best_type = "option"
                    self.components.rollback_transaction()

        if self.config.log and best_score:
            print('Found {} that would give score {}'.format(best_st, best_score - current_score))

        if best_score is None:
            # choose random if nothing found
            index = random.randint(0, len(all_edges) - 1)
            st = all_edges[index]
            return st, "claim"

        # raw_input("press enter")

        return best_st, best_type

    def _select_2_greedy_edges(self):
        # take 1 greedy then the other just anything
        s, t = self._select_greedy_edge()
        route = [s, t]
        for next in self.graph[t]:
            if next != s:
                route.append(next)
                break
        if self.config.log:
            print 'Returning route: {}'.format(route)
        return route



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
            def process_edge(punter_id, s, t):
                st = (s,t)
                remove_edge(self.graph, st)

                if punter_id == self.punter_id:
                    add_edge(self.my_graph, st)

                    self.components.start_transaction()
                    self.components.union(s, t)

                if self.settings.get("options", False):
                    if punter_id != self.punter_id:
                        self.available_for_option.add( (s, t) )
                        self.available_for_option.add( (t, s) )

            for move in data["move"]["moves"]:
                if "pass" in move:
                    punter_id = move["pass"]["punter"]
                    if punter_id == self.punter_id:
                        self.my_credit += 1

                if "claim" in move:
                    s = move["claim"]["source"]
                    t = move["claim"]["target"]
                    punter_id = move["claim"]["punter"]
                    process_edge(punter_id, s, t)

                if "splurge" in move:
                    splurges = move["splurge"]["route"]
                    punter_id = move["splurge"]["punter"]
                    for i in xrange(len(splurges) - 1):
                        s = splurges[i]
                        t = splurges[i + 1]
                        process_edge(punter_id, s, t)
                    if punter_id == self.punter_id:
                        self.my_credit -= (len(splurges) - 2)

                if "option" in move:
                    s = move["option"]["source"]
                    t = move["option"]["target"]
                    punter_id = move["option"]["punter"]

                    # if someone claimed this as option then we cannot take it
                    # anymore
                    self.available_for_option.discard( (s, t) )
                    self.available_for_option.discard( (t, s) )
                    if punter_id == self.punter_id:
                        self.my_options -= 1
                        st = (s, t)
                        add_edge(self.my_graph, st)
                        self.components.start_transaction()
                        self.components.union(s, t)



        if self.config.use_splurges and self.settings.get("splurges"):
            # splurges mode
            if self.my_credit > 0:
                route = self._select_2_greedy_edges()
                return {
                    "splurge": {
                        "punter": self.punter_id,
                        "route": route,
                    }
                }
            else:
                return {
                    "pass": {
                        "punter": self.punter_id,
                    }
                }

        # take one at random
        if self.num_moves == 1:
            s, t = self._select_random_edge(self.graph)
            if self.config.log:
                print 'Move: {}, got random move {}'.format(self.num_moves, (s, t))
        else:
            start = timer()
            (s, t), t_type = self._select_greedy_edge()
            end = timer()

            if t_type == "option":
                return {
                    "option": {
                        "punter": self.punter_id,
                        "source": s,
                        "target": t,
                    }
                }

            if self.config.log:
                print('Finished select_greedy_edge in {}s'.format(end - start))

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

    punter = FastGreedyPunter(config)
    client = Client(LOCALHOST, 9999)
    client.run(punter)