import math
from copy import deepcopy
from time import time, sleep
from pprint import pprint
from collections import deque, defaultdict
from random import shuffle, randint, choice

class VladSolver4:
    def __init__(self, config):
        self.name = config.name
        self.log = getattr(config, 'log', False)
        self.timeout = getattr(config, 'timeout', 0.95)
        self.add_own_move = getattr(config, 'add_own_move', False)
        self.score_regularization = getattr(config, 'score_regularization', True)
        self.max_of = getattr(config, 'max_of', 'min')

    def _list_greedy(self, id, log=False):
        # TODO: consider preach, instead of padj
        candidates = [(u,v) for (u,v) in self.free_edges
                                if ((u in self.padj[id]) or
                                    (v in self.padj[id]) or
                                    (u in self.mines) or (v in self.mines))]
        if log:
            pprint(candidates)
        if len(candidates) == 0:
            rnd = list(self.free_edges); shuffle(rnd)
            candidates = rnd[0:50]

        score_by_mine = {}
        for m in self.mines:
            res = self._bfs(m, self.padj[id])
            score_by_mine[m] = sum([self.dist[m][u]**2 for (u,_) in res.items()])

        ordered_edges = []
        for u,v in candidates:
            score = 0
            for m in self.mines:
                score += score_by_mine[m]
                if (u in self.preach[id][m]) and (v not in self.padj[id]):
                    score += self.dist[m][v]**2
                elif (v in self.preach[id][m]) and (u not in self.padj[id]):
                    score += self.dist[m][u]**2
                elif (u not in self.preach[id][m]) and (v not in self.preach[id][m]):
                    score += 0
                elif (u in self.preach[id][m]) and (v in self.preach[id][m]):
                    score += 0
                else:
                    res = self._bfs(m, self.padj[id], xtra={u:v, v:u})
                    newsc = sum([self.dist[m][xxu]**2 for (xxu,_) in res.items()])
                    assert newsc >= score_by_mine[m]
                    score += newsc - score_by_mine[m]
            ordered_edges.append( (score, (u,v)) )

        ordered_edges.sort(reverse=True)
        return ordered_edges


    def _own_greedy_response(self, adj, free_edges, num_moves_left):
        candidates = [(u,v) for (u,v) in free_edges
                                if ((u in adj) or
                                    (v in adj) or
                                    (u in self.mines) or (v in self.mines))]
        if len(candidates) == 0:
            rnd = list(free_edges); shuffle(rnd)
            candidates = rnd[0:10]

        best = (-1.0, candidates[0])
        for (u,v) in candidates:
            sc = self._eval(adj, xtra={u:v, v:u})
            best = max(best, (sc, (u,v)))
        (u,v) = best[1]

        # apply:
        adj[u].append(v);            adj[v].append(u)
        free_edges.discard( (u,v) ); free_edges.discard( (v,u) )

    def _try_move(self, u, v, adj, free_edges, num_moves_left):
        scores = [0.0 for id in xrange(self.num)]

        id = self.id

        # apply move
        adj[u].append(v);            adj[v].append(u)
        free_edges.discard( (u,v) ); free_edges.discard( (v,u) )
        num_moves_left -= 1
        id = (id + 1) % self.num

        # non-self greedy responses:
        while num_moves_left > 0 and id != self.id:
            mu = -1
            if randint(0, 100) < 10:
                (s, (mu, mv)) = choice(self.pgreedy[id])
            else:
                for (s, (u,v)) in self.pgreedy[id]:
                    if (u,v) in free_edges:
                        mu,mv = u,v
                        break
            if mu < 0:
                mu, mv = choice(list(free_edges))
                s = 0

            scores[id] += s
            free_edges.discard( (mu,mv) ); free_edges.discard( (mv,mu) )
            num_moves_left -= 1
            id = (id + 1) % self.num

        # own extra response:
        if num_moves_left > 0 and self.add_own_move:
            # TODO
            self._own_greedy_response(adj, free_edges, num_moves_left)
            num_moves_left -= 1

        scores[self.id] = self._eval(adj) + 0.0
        if self.score_regularization:
            scores = [s + 50.0 for s in scores]
        ss = max(sum(scores), 1e-9)
        return [s/ss for s in scores]


    def _eval(self, adj, xtra={}):
        score = 0
        for m in self.mines:
            res = self._bfs(m, adj, xtra)
            score += sum([self.dist[m][u]**2 for (u,_) in res.items()])
        return score


    def _compute_distances(self):
        for mine in self.mines:
            self.dist[mine] = self._bfs(mine, self.adj)

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

    def _org_bfs(self, mine, adj, xtra={}):
        tt = time()
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
        pprint(time() - tt)
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

        #pprint(self.free_edges)

        # mine reachability for each player
        self.preach = [{} for i in range(self.num)]
        for id in range(self.num):
            for m in self.mines:
                self.preach[id][m] = self._bfs(m, self.padj[id])

        # greedy-ordered moves for each non-self-player
        self.pgreedy = [[] for i in range(self.num)]
        for id in range(self.num):
            self.pgreedy[id] = self._list_greedy(id, False)

        # TODO: Filtering not necessarily desirable
        candidates = self.pgreedy[self.id]
        candidates = [(u,v) for (_,(u,v)) in candidates
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
                    u, v, deepcopy(self.padj[self.id]), deepcopy(self.free_edges),
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
