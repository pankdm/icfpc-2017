import time
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
    result = {start : 0}

    q = deque()
    q.append(start)
    while q:
        cur = q.popleft()
        value = result[cur]

        for nxt in graph.get(cur, set()):
            if nxt not in result:
                result[nxt] = value + 1
                q.append(nxt)
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

c_timeout = 4.5

# compute the scores to each city
# map : city -> city -> score
def compute_all_distances(world):
    begin = time.clock()
    distances = defaultdict(dict)
    for mine in world.vertices:
        distances[mine] = dict()
    for mine in world.mines:
        scores = run_bfs(mine, world.graph)
        for city, score in scores.items():
            distances[city][mine] = score
    for mine in world.vertices:
        if time.clock() - begin > c_timeout:
            break
        if not mine in world.mines:
            scores = run_bfs(mine, world.graph)
            for city, score in scores.items():
                distances[city][mine] = score
    return distances

def compute_bridge_scores(world, all_distances):
    begin = time.clock()
    result = {}
    for st, fs in world.graph.iteritems():
        for f in fs:
            result[ (st, f) ] = 0
            result[ (f, st) ] = 0

    for st, fs in world.graph.iteritems():
        if time.clock() - begin > c_timeout:
            break

        for f in fs:
            for mine in world.mines:
                if mine in all_distances[st] and mine in all_distances[f]:
                    dst = all_distances[st][mine]
                    df = all_distances[f][mine]
                    for v in world.mines:
                        if mine in all_distances[v]:
                            dv = all_distances[v][mine]
                            if dv == dst + all_distances[f][v] + 1 or dv == df + all_distances[st][v] + 1:
                                result[ (st, f) ] += 1
                                result[ (f, st) ] += 1
    return result


def compute_vertices_centralness(world, all_distances):
    max_distance_sum = 0
    sum_distances = {}
    for u in world.vertices:
        distance_sum = 0
        for v in world.vertices:
            if u != v:
                if v in all_distances[u]:
                    distance_sum += all_distances[u][v]
                else:
                    distance_sum += 3*world.n
        sum_distances[u] = distance_sum
        max_distance_sum = max(max_distance_sum, distance_sum)
    for u, distance_sum in sum_distances.iteritems():
       sum_distances[u] = (float(max_distance_sum) - float(distance_sum))/float(max_distance_sum)
    return sum_distances

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
