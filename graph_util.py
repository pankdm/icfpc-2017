
from collections import defaultdict, deque


def add_edge(graph, st):
    s, t = st
    graph[s].add(t)
    graph[t].add(s)


class World:
    def __init__(self, map_data):
        self.graph = defaultdict(set)
        for river in map_data["rivers"]:
            s = river["source"]
            t = river["target"]

            # assume no multiedges for now
            assert t not in self.graph[s]
            assert s not in self.graph[t]

            self.graph[s].add(t)
            self.graph[t].add(s)

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
