import math
from copy import deepcopy
from time import time
from pprint import pprint
from collections import deque, defaultdict
from random import shuffle

class Node:
    def __init__(self):
        self.nsimul = 0
        self.score = 0
        self.vchild = []
        self.uchild = deque()


class VladSolver1:
    def __init__(self, config):
        self.name = config.name
        self.timeout = getattr(config, 'timeout', 0.95)

    def _get_node(self, padj, id, num_moves_left, free_edges):
        h = hash(repr((padj,id, num_moves_left)))
        if h in self.tr:
            return self.tr[h]
        else:
            node = Node()
            node.uchild = deque(free_edges)
            self.tr[h] = node
            return node

    def _mcts_iter(self, root, padj, free_edges, num_moves_left):
        id = self.id
        path = [root]

        while num_moves_left > 0 and root.nsimul > 0:
            if len(root.uchild) > 0:
                (u,v) = root.uchild.popleft()
                padj[id][u].append(v)
                padj[id][v].append(u)
                free_edges.discard((u,v))
                free_edges.discard((v,u))
                
                node = self._get_node(padj, (id + 1) % self.num, num_moves_left - 1, free_edges)
                root.vchild.append([(u,v), node, 1])
                root = node
            else:
                assert len(root.vchild) > 0
                opts = []
                for i in range(len(root.vchild)):
                    cnode = root.vchild[i][1]
                    ccnt = root.vchild[i][2]
                    sc = (cnode.score + 0.0) / cnode.nsimul + 1.41 * math.sqrt( math.log(root.nsimul) / ccnt )
                    opts.append( (sc, i) )
                i = max(opts)[1]

                (u,v) = root.vchild[i][0]   # "apply" selected move
                padj[id][u].append(v)
                padj[id][v].append(u)
                root.vchild[i][2] += 1      # update edge stat
                root = root.vchild[i][1]    # advance

            path.append(root)
            id = (id + 1) % self.num
            num_moves_left -= 1

        #if num_moves_left == 0:
        #    # TODO leaf node ?!

        scores = self._mcts_playout(root, id, padj, free_edges, num_moves_left)

        id = self.id
        for node in path:
            node.nsimul += 1
            node.score += scores[id]
            id = (id + 1) % self.num

    def _mcts_playout(self, root, id, padj, free_edges, num_moves_left):
        rnd_edges = list(free_edges)
        shuffle(rnd_edges)

        for (u,v) in rnd_edges:
            if num_moves_left == 0:
                break
            num_moves_left -= 1
            padj[id][u].append(v)
            padj[id][v].append(u)
            id = (id + 1) % self.num
        
        scores = []
        for id in range(self.num):
            score = 0
            for m in self.mines:
                res = self._bfs(m, padj[id])
                score += sum([d*d for (_,d) in res.items()])
            scores.append(score)
        return scores

    def _compute_distances(self):
        for mine in self.mines:
            self.dist[mine] = self._bfs(mine, self.adj)

    def _bfs(self, mine, adj):
        q = deque()
        q.append((mine, 0))
        res = {}

        while len(q) > 0:
            u, d = q.popleft()
            if u not in res:
                res[u] = d

            for v in adj[u]:
                if v not in res:
                    q.append((v, d+1))
        return res

    def get_handshake(self):
        return {'me': 'vlad1'}

    def process_setup(self, data):
        self.id = data['punter']
        self.num = data['punters']
        self.adj = {}
        self.mines = []
        self.dist = {}
        self.tr = {}
        self.free_edges = set([])

        for site in data['map']['sites']:
            id = site['id']
            self.adj[id] = []

        for edge in data['map']['rivers']:
            u = edge['source']
            v = edge['target']
            self.adj[u].append(v)
            self.adj[v].append(u)
            self.free_edges.add( tuple(sorted((u,v))) )
        
        for mine in data['map']['mines']:
            self.mines.append(mine)

        self._compute_distances()

        self.padj = {i: defaultdict(list) for i in range(self.num)}
        self.num_moves_left = len(data['map']['rivers'])

        pprint(self.id)
        pprint(self.num)
        pprint(self.adj)
        pprint(self.mines)
        pprint(self.dist)
        pprint(self.free_edges)
        pprint(self.padj)
        pprint(self.num_moves_left)

        return {'ready': self.id}

    def process_stop(self, data):
        pprint(data)

    def process_move(self, data):
        tbegin = time()

        if 'stop' in data:
            self.process_stop(data)
            return

        for mv in data['move']['moves']:
            if 'claim' in mv:
                id = mv['claim']['punter']
                (u,v) = (mv['claim']['source'], mv['claim']['target'])
                self.padj[id][u].append(v)
                self.padj[id][v].append(u)
                self.free_edges.discard( (u,v) )
                self.free_edges.discard( (v,u) )
                self.num_moves_left -= 1

        self.tr = {}
        root = self._get_node(
                self.padj,
                self.id,
                self.num_moves_left,
                self.free_edges)

        while time() < tbegin + self.timeout:
            self._mcts_iter(
                root,
                deepcopy(self.padj),
                deepcopy(self.free_edges),
                self.num_moves_left)

        opts = []
        for i in range(len(root.vchild)):
            cnode = root.vchild[i][1]
            ccnt = root.vchild[i][2]
            sc = (cnode.score + 0.0) / cnode.nsimul
            opts.append( (sc, i) )

        i = max(opts)[1]
        (u,v) = root.vchild[i][0]   # best move (haha)

        pprint("MCTS: nsimul {}; time {}; move: {}".format(
            root.nsimul, time() - tbegin, (u,v)))

        return {'claim': {'punter': self.id, 'source': u, 'target': v}}
