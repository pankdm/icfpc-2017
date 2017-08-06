from copy import deepcopy

class UnionFindFast:
    def __init__(self, n, mines, distances):
        self.mines_ = mines
        self.distances_ = distances
        self.scores_ = [ [ x**2 for x in v.values() ] for v in distances.values() ]
        self.id_ = [ i for i in xrange(n) ]
        self.sz_ = [ 1 ] * n
        self.mn_ = [ [ (mines.index(i), i) ] if i in mines else [] for i in xrange(n) ]
        self.totals_ = [ 0 ] * n
        self.score_ = 0

    def union(self, i, j):
        ri = self.root(i)
        rj = self.root(j)
        if ri == rj:
            return
        if (self.sz_[ri] < self.sz_[rj]):
            ri, rj = rj, ri

        self.score_ -= self.totals_[ri]
        self.score_ -= self.totals_[rj]

        for (index, mine) in self.mn_[ri]:
            self.totals_[ri] += self.scores_[rj][index]

        for (index, mine) in self.mn_[rj]:
            self.totals_[ri] += self.scores_[ri][index]

        self.totals_[ri] += self.totals_[rj]
        self.score_ += self.totals_[ri]

        self.id_[rj] = ri
        self.sz_[ri] += self.sz_[rj]
        self.mn_[ri] += self.mn_[rj]
        for k in xrange(len(self.mines_)):
            self.scores_[ri][k] += self.scores_[rj][k]

    def find(self, i, j):
        return root(i) == root(j)

    def root(self, i):
        while (i != self.id_[i]):
            self.id_[i] = self.id_[self.id_[i]]
            i = self.id_[i]
        return i

    def score(self):
        return self.score_
        '''score = 0
        for index, mine in enumerate(self.mines_):
            root = self.root(mine)
            score += self.scores_[root][index]
        return score'''

    def copy(self):
        u = UnionFindFast(len(self.id_), self.mines_, self.distances_)
        u.scores_ = deepcopy(self.scores_)
        u.id_ = deepcopy(self.id_)
        u.sz_ = deepcopy(self.sz_)
        u.mn_ = deepcopy(self.mn_)
        u.totals_ = deepcopy(self.totals_)
        u.score_ = score_
        return u

    def __str__(self):
        return "\n".join([
            'id ' + str(self.id_),
            'sz ' + str(self.sz_),
            'mines ' + str(self.mines_),
            'scores ' + str(self.scores_),
            'totals ' + str(self.totals_),
            'mn ' + str(self.mn_), 
            'score() ' + str(self.score()),
            'score ' + str(self.score_),
        ])

if __name__ == "__main__":
    cl = UnionFindFast(8, [1, 5], {0: {1: 1, 5: 2}, 1: {1: 0, 5: 2}, 2: {1: 1, 5: 2}, 3: {1: 1, 5: 1}, 4: {1: 2, 5: 1}, 5: {1: 2, 5: 0}, 6: {1: 2, 5: 1}, 7: {1: 1, 5: 1}})
    print(cl)
    cl.union(0, 1)
    print
    print(cl)
    cl.union(0, 2)
    print
    print(cl)
    cl.union(1, 2)
    print
    print(cl)
    cl.union(1, 3)
    print
    print(cl)
    cl.union(2, 4)
    print
    print(cl)
    cl.union(6, 5)
    print
    print(cl)
    cl.union(3, 6)
    print
    print(cl)
    cl.union(3, 6)
    print
    print(cl)
    cl.union(1, 7)
    print
    print(cl)
    print
    print(deepcopy(cl))