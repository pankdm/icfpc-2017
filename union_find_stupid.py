from copy import deepcopy

class UnionFindStupid:
    def __init__(self, n):
        if n == None:
            return
        # each one points to itself initially
        self.root_ = [i for i in xrange(n)]
        self.lists_ = []
        for i in range(n):
            self.lists_.append(set())
            self.lists_[i].add(i)

    def union(self, s, t):
        rs = self.root_[s]
        rt = self.root_[t]

        # optimization
        if len(self.lists_[rs]) > len(self.lists_[rt]):
            rs, rt = rt, rs

        # now rs has smaller size so it will be faster to move from it
        for node in self.lists_[rs]:
            self.lists_[rt].add(node)
            self.root_[node] = rt

        self.lists_[rs] = set()

    def root(self, v):
        return self.root_[v]

    def nodes_in_component(self, v):
        root = self.root_[v]
        return self.lists_[root]

    def copy(self):
        u = UnionFindStupid(None)
        u.root_ = deepcopy(self.root_)
        u.lists_ = deepcopy(self.lists_)
        return u
