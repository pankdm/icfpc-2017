import math
from copy import deepcopy
from time import time, sleep
from pprint import pprint
from collections import deque, defaultdict
from random import shuffle, randint

class Node:
    def __init__(self):
        self.nsimul = 0
        self.score = 0
        self.vchild = []
        self.uchild = deque()


class VladSolver2:
    def __init__(self, config):
        self.name = config.name
        self.timeout = getattr(config, 'timeout', 0.95)
        self.log = getattr(config, 'log', False)
        self.sum_norm = getattr(config, 'sum_norm', True)
        self.playout_max_depth = getattr(config, 'playout_max_depth', 9999)
        self.search_width = getattr(config, 'search_width', 9999)
        self.magic_moves = getattr(config, 'magic_moves', False)
        self.greedy_threshold = getattr(config, 'greedy_threshold', 9999)

    def _get_node(self, padj, id, num_moves_left, free_edges):
        h = hash(repr((padj,id, num_moves_left)))
        if h in self.tr:
            return self.tr[h]
        else:
            node = Node()
            if self.magic_moves:
                node.uchild = self._magic_moves(free_edges, id, padj, self.search_width)
            else:
                rnd_edges = list(free_edges); shuffle(rnd_edges)
                node.uchild = deque(rnd_edges[0:self.search_width])
            self.tr[h] = node
            return node

    def _magic_moves(self, free_edges, id, padj, width):
        se = []
        for (u,v) in free_edges:
            sc = 1

            # mine heuristic:
            if u in self.mines:
                sc += 15
                if (u not in padj[id]) and (self.sum_mine_sc[u] >= 5):
                    sc += 100
                if v in padj[id]:
                    sc += 12
            if v in self.mines:
                sc += 15
                if (v not in padj[id]) and (self.sum_mine_sc[v] >= 5):
                    sc += 100
                if u in padj[id]:
                    sc += 12

            # site heuristic
            #sc += self.sum_dist_sc[u] / 2
            #sc += self.sum_dist_sc[v] / 2

            # adjacent to own edges:
            if bool(v in padj[id]) ^ bool(u in padj[id]):
                sc += 8

            # add edge with score
            sc += randint(0, 10)
            se.append( (sc, (u,v)) )

        se.sort(reverse=True)
        return deque([e for (_,e) in se[0:width]])

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
                free_edges.discard((u,v))
                free_edges.discard((v,u))
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
            node.score += scores[(id - 1 + self.num) % self.num]
            id = (id + 1) % self.num

    def _mcts_playout(self, root, id, padj, free_edges, num_moves_left):
        rnd_edges = list(free_edges)
        shuffle(rnd_edges)

        num_played = 0
        for (u,v) in rnd_edges:
            if num_moves_left == 0:
                break
            if num_played >= self.playout_max_depth:
                break
            num_moves_left -= 1
            num_played += 1

            padj[id][u].append(v)
            padj[id][v].append(u)
            id = (id + 1) % self.num
        
        return self._eval(padj)

    def _eval(self, padj):
        scores = []
        for id in range(self.num):
            score = 0
            for m in self.mines:
                res = self._bfs(m, padj[id])
                score += sum([d*d for (_,d) in res.items()])
            scores.append(score)
        if self.sum_norm:
            mx = sum(scores) + 0.0
        else:
            mx = max(scores) + 0.0
        return [s / max([mx, 0.001]) for s in scores]

    def _compute_distances(self):
        for mine in self.mines:
            self.dist[mine] = self._bfs(mine, self.adj)
            # for heuristics:
            for (u, d) in self.dist[mine].items():
                if d <= 5:
                    self.sum_dist_sc[u] += d*d
            self.sum_mine_sc[mine] = sum([d*d for (_,d) in self.dist[mine].items() if d <= 10])

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
        return {'me': self.name}

    def process_setup(self, data):
        self.id = data['punter']
        self.num = data['punters']
        self.adj = {}
        self.mines = set([])
        self.dist = {}
        self.sum_dist_sc = defaultdict(lambda: 0)
        self.sum_mine_sc = {}
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
            self.mines.add(mine)

        self._compute_distances()

        self.padj = {i: defaultdict(list) for i in range(self.num)}
        self.num_moves_left = len(data['map']['rivers'])

        #pprint(self.id)
        #pprint(self.num)
        #pprint(self.adj)
        #pprint(self.mines)
        #pprint(self.dist)
        #pprint(self.free_edges)
        #pprint(self.padj)
        #pprint(self.num_moves_left)

        return {'ready': self.id}

    def process_stop(self, data):
        #pprint(data)
        return

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

        has_move = False
        if self.num_moves_left > self.greedy_threshold:
            mvs = self._magic_moves(self.free_edges, self.id, self.padj, 200)
            if len(mvs) > 0:
                se = []
                for (u,v) in mvs:
                    padj = deepcopy(self.padj)
                    padj[self.id][u].append(v)
                    padj[self.id][v].append(u)
                    se.append( (self._eval(padj)[self.id], (u,v)) )
                se.sort(reverse=True)
                (u, v) = se[0][1]
                has_move = True
                if self.log:
                    pprint("Grdy {} /{}: time {}; move: {}".format(
                        self.name, self.num_moves_left, time() - tbegin, (u,v)))

        if not has_move:
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
                sc = (cnode.score + 0.0) / cnode.nsimul
                opts.append( (sc, i) )

            i = max(opts)[1]
            (u,v) = root.vchild[i][0]   # best move (haha)

            if self.log:
                pprint("MCTS {} /{}: nsimul {}; time {}; move: {}".format(
                    self.name, self.num_moves_left, root.nsimul, time() - tbegin, (u,v)))

        return {'claim': {'punter': self.id, 'source': u, 'target': v}}
