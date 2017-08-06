
from collections import defaultdict, deque


def add_edge(graph, st):
    s, t = st
    graph[s].add(t)
    graph[t].add(s)

def remove_edge(graph, st):
    s, t = st
    graph[s].remove(t)
    graph[t].remove(s)


class World:
    def __init__(self, map_data):
        self.graph = defaultdict(set)
        self.vertices = set()
        self.n = 0
        for river in map_data["rivers"]:
            s = river["source"]
            t = river["target"]

            # assume no multiedges for now
            assert t not in self.graph[s]
            assert s not in self.graph[t]

            self.graph[s].add(t)
            self.graph[t].add(s)

            self.vertices.add(s)
            self.vertices.add(t)
            self.n = max(self.n, s, t)
        self.n += 1

        self.mines = set()
        for mine in map_data["mines"]:
            self.mines.add(mine)


# runs bfs from the start and returns map of distances from it
def run_bfs(start, graph):
    q = deque()

    q.append(start)
    result = {start : 0}

    while q:
        cur = q.popleft()
        value = result[cur]

        for next in graph.get(cur, set()):
            if next not in result:
                result[next] = value + 1
                q.append(next)
    return result

# compute the scores to each city
# map : city -> mine -> score
def compute_distances(world):
    distances = defaultdict(dict)
    for mine in world.mines:
        scores = run_bfs(mine, world.graph)
        for city, score in scores.items():
            distances[city][mine] = score
    return distances


# compute the scores to each city
# map : city -> city -> score
def compute_all_distances(world):
    distances = defaultdict(dict)
    for mine in world.vertices:
        scores = run_bfs(mine, world.graph)
        for city, score in scores.items():
            distances[city][mine] = score
    return distances


def floyd_warshall(graph):
    n = 0
    for s, ts in graph.iteritems():
        n = max(n, s)
        for t in ts:
            n = max(n, t)
    n += 1
    distances = [ [10000000]*n for _ in xrange(n) ]
    for s, ts in graph.iteritems():
        for t in ts:
            distances[s][t] = 1
            distances[t][s] = 1
    for k in xrange(n):
        for i in xrange(n):
            for j in xrange(n):
                di[i][j] = min(distances[i][j], distances[i][k] + distances[k][j])
    return distances
