from pprint import pprint
from collections import deque

class VladSolver1:

    def _compute_distances():
        for mine in self.mines:
            self.dist[mine] = _bfs(mine)

    def _bfs(mine):
        q = deque()
        q.append((mine, 0))
        res = {}

        while q.count() > 0:
            u, d = q.popleft()
            if u not in res:
                res[u] = d

            for v in self.adj[u]:
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

        for site in data['map']['sites']:
            id = site['id']
            self.adj[id] = []

        for edge in data['map']['rivers']:
            u = edge['source']
            v = edge['target']
            self.adj[u].append(v)
            self.adj[v].append(u)
        
        for mine in data['map']['mines']:
            self.mines.append(mine)

        _compute_distances()

        pprint(self.id)
        pprint(self.num)
        pprint(self.adj)
        pprint(self.mines)
        pprint(self.dist)

        return {'ready': self.id}

    def process_stop(self, data):
        pprint(data)

    def process_move(self, data):
        if 'stop' in data:
            self.process_stop(data)
            return
        return {'pass': {'punter', self.id}}

