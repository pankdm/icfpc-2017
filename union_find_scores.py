import random

class ComponentsListWithScores:
    def __init__(self, n, mines, distances, bridge_scores = {}, vertex_scores = {}):
        self.lists_ = []
        self.vertices_ = []
        for i in range(n):
            self.lists_.append(set())
            self.lists_[i].add(i)
            self.vertices_.append(i)
        self.score_ = 0
        self.mines_ = mines
        self.distances_ = distances
        self.bridge_scores_ = bridge_scores
        self.vertex_scores_ = vertex_scores
        self.edges_ = set()
        self.bridge_score_ = 0
        self.vertex_score_ = 0
        self.added_vertices_ = set()
        
        self.transactions_ = []
        self.transctions_scores_ = []
        self.transctions_edges_ = []
        self.transactions_bridge_scores_ = []
        self.transactions_vertex_scores_ = []
        self.transactions_vertices_ = []

    def union(self, i, j):
        if i > j:
            i, j = j, i
        self.edges_.remove( (i, j) )
        self.transctions_edges_[-1].append( (i, j) )
        self.add_vertex(i)
        self.add_vertex(j)

        if (i, j) in self.bridge_scores_:
            self.bridge_score_ += self.bridge_scores_[(i, j)]

        i = self.component(i)
        j = self.component(j)
        for x in self.lists_[i]:
            if x in self.mines_:
                for y in self.lists_[j]:
                    self.score_ += self.distances_.get(y, {}).get(x, 0)**2
        for x in self.lists_[j]:
            if x in self.mines_:
                for y in self.lists_[i]:
                    self.score_ += self.distances_.get(y, {}).get(x, 0)**2
        for x in self.lists_[j]:
            self.add(i, x)
        for x in list(self.lists_[j]):
            self.remove(j, x)

    def add(self, component, v):
        self.transactions_[-1].append( ('-', v, component) )
        self.transactions_[-1].append( ('+', v, self.vertices_[v]) )
        self.lists_[component].add(v)
        self.vertices_[v] = component

    def add_vertex(self, v):
        if not v in self.added_vertices_:
            self.added_vertices_.add(v)
            self.transactions_vertices_[-1].append( ('-', v) )
            if v in self.vertex_scores_:
                self.vertex_score_ += self.vertex_scores_[v]

    def remove(self, component, v):
        self.transactions_[-1].append( ('+', v, component) )
        self.lists_[component].remove(v)

    def start_transaction(self):
        self.transactions_.append([])
        self.transctions_scores_.append(self.score_)
        self.transctions_edges_.append([])
        self.transactions_bridge_scores_.append(self.bridge_score_)
        self.transactions_vertex_scores_.append(self.vertex_score_)
        self.transactions_vertices_.append([])

    def rollback_transaction(self):
        for e in self.transctions_edges_[-1]:
            self.edges_.add(e)
        self.transctions_edges_.pop()

        for t in self.transactions_[-1]:
            if t[0] == '+':
                self.lists_[t[2]].add(t[1])
                self.vertices_[t[1]] = t[2]
            else:
                self.lists_[t[2]].remove(t[1])
        self.transactions_.pop()
        
        self.score_ = self.transctions_scores_[-1]
        self.transctions_scores_.pop()
        
        self.bridge_score_ = self.transactions_bridge_scores_[-1]
        self.transactions_bridge_scores_.pop()

        self.vertex_score_ = self.transactions_vertex_scores_[-1]
        self.transactions_vertex_scores_.pop()

        for t in self.transactions_vertices_[-1]:
            if t[0] == '+':
                self.added_vertices_.add(t[1])
            else:
                self.added_vertices_.remove(t[1])
        self.transactions_vertices_.pop()


    def component(self, v):
        return self.vertices_[v]

    def components(self):
        return self.lists_

    def score(self):
        return self.score_

    def bridge_score(self):
        return self.bridge_score_

    def vertex_score(self):
        return self.vertex_score_

    def add_edge(self, s, t):
        if s > t:
            s, t = t, s
        self.edges_.add( (s, t) )

    def remove_edge(self, s, t):
        if s > t:
            s, t = t, s
        self.edges_.remove( (s, t) )

    def num_edges(self):
        return len(self.edges_)

    def random_edge(self):
        result = None
        i = 0
        for x in self.edges_:
            if not result or random.random() * len(self.edges_) < 1.0:
                result = x
            i += 1
            if i > 50:
                break
        return result

if __name__ == "__main__":
    cl = ComponentsList(5)
    cl.start_transaction()
    cl.union(1, 2)
    print('1', cl.components()[1])
    print('1a', cl.components()[2])
    print('comp 1', cl.component(1))
    print('comp 2', cl.component(2))
    cl.start_transaction()
    cl.union(3, 4)
    print('2', cl.components()[1])
    print('3', cl.components()[3])
    cl.start_transaction()
    cl.union(1, 3)
    print('4', cl.components()[1])
    print('5', cl.components()[3])
    print('comp 3', cl.component(3))
    print('comp 4', cl.component(4))
    cl.rollback_transaction()
    print('6', cl.components()[1])
    cl.rollback_transaction()
    print('7', cl.components()[1])
    cl.rollback_transaction()
    print('8', cl.components()[1])
