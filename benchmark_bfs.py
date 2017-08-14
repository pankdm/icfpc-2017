import sys
from collections import defaultdict, deque
import json
from timeit import default_timer as timer


def run_bfs(start, graph):
    result = {start : 0}

    q = deque()
    q.append(start)

    counter = 0
    while q:
        counter += 1
        cur = q.popleft()
        value = result[cur]

        for nxt in graph.get(cur, set()):
            if nxt not in result:
                result[nxt] = value + 1
                q.append(nxt)
    # print 'In run_bfs counter = {}'.format(counter)
    return result

def run_slow_bfs(start, graph):
    q = deque()
    q.append((start, 0))
    result = {}

    counter = 0
    while q:
        counter += 1
        cur, value = q.popleft()
        if cur not in result:
            result[cur] = value
        for nxt in graph.get(cur, set()):
            if nxt not in result:
                result[nxt] = value + 1  # Magic Line
                q.append((nxt, value + 1))
    # print 'In run_slow_bfs counter = {}'.format(counter)
    return result

def run_with_timer(mines, graph, bfs):
    start = timer()
    for v in mines:
        bfs(v, graph)
        # break
    end = timer()
    print ('Function {} took {}s'.format(bfs.__name__, end - start))



def read_graph(map_file):
    map_data = json.loads(open(map_file, 'rt').read())
    graph = defaultdict(set)
    for river in map_data["rivers"]:
        s = river["source"]
        t = river["target"]

        graph[s].add(t)
        graph[t].add(s)

    mines = set()
    for mine in map_data["mines"]:
        mines.add(mine)

    return graph, mines

def run():
    map_file = sys.argv[1]
    graph, mines = read_graph(map_file)

    while True:
        print
        run_with_timer(mines, graph, run_bfs)
        run_with_timer(mines, graph, run_slow_bfs)


if __name__ == "__main__":
    run()
