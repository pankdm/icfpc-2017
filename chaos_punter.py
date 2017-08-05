from collections import defaultdict
from copy import deepcopy
import random
from pprint import pprint

from config import Config

from client import *
from graph_util import *

class ChaosPunter:
    def __init__(self, config):
        self.name = "chaos monkey" if not config.name else config.name
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

        # default reply
        reply = {"ready": self.punter_id}

        if self.config.futures:
            futures = data.get("settings", {}).get("futures", False)
            if futures:
                s, t = self._select_random_future(self.graph)
                print('Selected future: {}'.format((s, t)))
                reply["futures"] = [{
                    "source": s,
                    "target": t
                }]
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
            if self.config.log:
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
                    remove_edge(self.graph, (s,t))

        # take one at random
        s, t = self._select_random_edge(self.graph)
        if self.config.log:
            print('Move: {}, got random move {}'.format(self.num_moves, (s,t)))

        return {
            "claim": {
                "punter": self.punter_id,
                "source": s,
                "target": t,
            },
        }

if __name__ == "__main__":
    config = Config()
    config.log = False

    punter = ChaosPunter(config)
    client = Client(LOCALHOST, 9999)
    client.run(punter)
