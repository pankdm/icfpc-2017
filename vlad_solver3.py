import math
from copy import deepcopy
from time import time, sleep
from pprint import pprint
from collections import deque, defaultdict
from random import shuffle, randint

class VladSolver3:
    def __init__(self, config):
        self.name = config.name
        self.log = getattr(config, 'log', False)
        self.timeout = getattr(config, 'timeout', 0.95)
        self.add_own_move = getattr(config, 'add_own_move', True)
        self.score_regularization = getattr(config, 'score_regularization', True)
        self.max_of = getattr(config, 'max_of', 'avg')

    def _apply_greedy_response(self, id, padj, free_edges, num_moves_left):
        candidates = [(u,v) for (u,v) in free_edges
                                if ((u in padj[id]) or
                                    (v in padj[id]) or
                                    (u in self.mines) or (v in self.mines))]
        if len(candidates) == 0:
            rnd = list(free_edges); shuffle(rnd)
            candidates = rnd[0:10]

        best = (-1.0, candidates[0])
        for (u,v) in candidates:
            #adj = deepcopy(padj[id])
            #adj[u].append(v); adj[v].append(u)
            sc = self._eval(padj[id], xtra={u:v, v:u})
            best = max(best, (sc, (u,v)))
        (u,v) = best[1]

        # apply:
        padj[id][u].append(v);       padj[id][v].append(u)
        free_edges.discard( (u,v) ); free_edges.discard( (v,u) )

    def _try_move(self, u, v, padj, free_edges, num_moves_left):
        id = self.id

        # apply move
        padj[id][u].append(v);       padj[id][v].append(u)
        free_edges.discard( (u,v) ); free_edges.discard( (v,u) )
        num_moves_left -= 1
        id = (id + 1) % self.num

        # greedy responses:
        while num_moves_left > 0 and id != self.id:
            self._apply_greedy_response(id, padj, free_edges, num_moves_left)
            num_moves_left -= 1
            id = (id + 1) % self.num

        # own extra response:
        if num_moves_left > 0 and self.add_own_move:
            self._apply_greedy_response(self.id, padj, free_edges, num_moves_left)
            num_moves_left -= 1

        scores = [self._eval(padj[id]) + 0.0 for id in xrange(self.num)]
        if self.score_regularization:
            scores = [s + 50.0 for s in scores]
        ss = max(sum(scores), 1e-9)
        return [s/ss for s in scores]


    def _eval(self, adj, xtra={}):
        score = 0
        for m in self.mines:
            res = self._bfs(m, adj, xtra)
            score += sum([self.dist[m][d]**2 for (_,d) in res.items()])
        return score


    def _compute_distances(self):
        for mine in self.mines:
            self.dist[mine] = self._bfs(mine, self.adj)

    def _bfs(self, mine, adj, xtra={}):
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
            if u in xtra:
                v = xtra[u]
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
        self.free_edges = set([])

        for site in data['map']['sites']:
            id = site['id']
            self.adj[id] = []

        for mine in data['map']['mines']:
            self.mines.add(mine)

        for edge in data['map']['rivers']:
            u = edge['source']
            v = edge['target']
            self.adj[u].append(v)
            self.adj[v].append(u)
            self.free_edges.add( tuple(sorted((u,v))) )

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
            # TODO: support multi-moves
            if 'claim' in mv:
                id = mv['claim']['punter']
                (u,v) = (mv['claim']['source'], mv['claim']['target'])
                self.padj[id][u].append(v)
                self.padj[id][v].append(u)
                self.free_edges.discard( (u,v) )
                self.free_edges.discard( (v,u) )
            self.num_moves_left -= 1

        # TODO: Filtering not necessarily desirable
        candidates = [(u,v) for (u,v) in self.free_edges
                                if ((u in self.padj[self.id]) or
                                    (v in self.padj[self.id]) or
                                    (u in self.mines) or (v in self.mines))]
        if len(candidates) == 0:
            rnd = list(self.free_edges); shuffle(rnd)
            candidates = rnd[0:10]

        cand_scores = [[] for _ in xrange(len(candidates))]

        nsimul = 0.0
        while time() < tbegin + self.timeout:
            for i, (u,v) in enumerate(candidates):
                sc = self._try_move(
                    u, v, deepcopy(self.padj), deepcopy(self.free_edges),
                    self.num_moves_left)[self.id]
                cand_scores[i].append(sc)
                nsimul += 1.0 / len(candidates)
                if time() >= tbegin + self.timeout:
                    break

        best = (-1.0, candidates[0])
        for i, (u,v) in enumerate(candidates):
            if len(cand_scores[i]) == 0:
                break

            if self.max_of == 'avg':
                best = max(best, (sum(cand_scores[i]) / len(cand_scores[i]), (u,v)))
            elif self.max_of == 'max':
                best = max(best, (max(cand_scores[i]), (u,v)))
            elif self.max_of == 'min':
                best = max(best, (min(cand_scores[i]), (u,v)))
            else:
                raise Exception("incorrect max_of")

        (u,v) = best[1]

        if self.log:
            pprint("- {} /{}: nsimul {:.2f} ({}); time {}; move: {}".format(
                self.name, self.num_moves_left, nsimul, len(candidates), time() - tbegin, (u,v)))

        return {'claim': {'punter': self.id, 'source': u, 'target': v}}
