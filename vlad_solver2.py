import math
from copy import deepcopy
from time import time, sleep
from pprint import pprint
from collections import deque, defaultdict
from random import shuffle, randint
import offline_punter

class Node:
    def __init__(self):
        self.nsimul = 0
        self.score = 0
        self.vchild = []
        self.uchild = deque()


class VladSolver2(offline_punter.OfflinePunter):
    def get_state(self):
        state = []
        state.append(self.name)
        state.append(self.timeout)
        state.append(self.log)
        state.append(self.sum_norm)
        state.append(self.playout_max_depth)
        state.append(self.search_width)
        state.append(self.magic_moves)
        state.append(self.greedy_threshold)
        state.append(self.id)
        state.append(self.num)
        state.append(self.adj)
        state.append(self.mines)
        state.append(self.dist)
        state.append(self.sum_dist_sc)
        state.append(self.sum_mine_sc)
        state.append(self.tr)
        state.append(self.free_edges)
        state.append(self.padj)
        state.append(self.num_moves_left)
        return state

    def set_state(self, state):
        self.name = state[0]
        self.timeout = state[1]
        self.log = state[2]
        self.sum_norm = state[3]
        self.playout_max_depth = state[4]
        self.search_width = state[5]
        self.magic_moves = state[6]
        self.greedy_threshold = state[7]
        self.id = state[8]
        self.num = state[9]
        self.adj = state[10]
        self.mines = state[11]
        self.dist = state[12]
        self.sum_dist_sc = state[13]
        self.sum_mine_sc = state[14]
        self.tr = state[15]
        self.free_edges = state[16]
        self.padj = state[17]
        self.num_moves_left = state[18]

    def __init__(self, config):
        self.name = config.name
        self.timeout = getattr(config, 'timeout', 0.9)
        self.log = getattr(config, 'log', False)
        self.sum_norm = getattr(config, 'sum_norm', True)
        self.playout_max_depth = getattr(config, 'playout_max_depth', 50)
        self.search_width = getattr(config, 'search_width', 15)
        self.magic_moves = getattr(config, 'magic_moves', True)
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
                score += sum([self.dist[m][u]**2 for (u,_) in res.items()])
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

    def _bfs(self, mine, adj, xtra={}):
        q = deque()
        q.append(mine)
        res = {mine: 0}
        while len(q) > 0:
            u = q.popleft()
            d = res[u]
            for v in adj[u]:
                if v not in res:
                    q.append(v)
                    res[v] = d + 1

            if u in xtra:
                v = xtra[u]
                if v not in res:
                    q.append(v)
                    res[v] = d + 1
        return res

    def _xbfs(self, mine, adj):
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
        self.sum_dist_sc = defaultdict(int)
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
            if 'splurge' in mv:
                id = mv['splurge']['punter']
                for i in range(1, len(mv['splurge']['route'])):
                    (u,v) = (mv['splurge']['route'][i-1], mv['splurge']['route'][i])
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

            if 0 != len(opts):
                i = max(opts)[1]
                (u,v) = root.vchild[i][0]   # best move (haha)
            else:
                if 0 != len(self.free_edges):
                    (u, v) = next(iter(self.free_edges))
                else:
                    return {'pass': {'punter': self.id}}

            if self.log:
                pprint("MCTS {} /{}: nsimul {}; time {}; move: {}".format(
                    self.name, self.num_moves_left, root.nsimul, time() - tbegin, (u,v)))

        self.tr = {}
        return {'claim': {'punter': self.id, 'source': u, 'target': v}}
