class ComponentsList:
    def __init__(self, n):
        self.lists_ = []
        self.vertices_ = []
        for i in range(n):
            self.lists_.append(set())
            self.lists_[i].add(i)
            self.vertices_.append(i)
        self.transactions_ = []

    def union(self, i, j):
        for x in self.lists_[j]:
            self.add(i, x)
        for x in list(self.lists_[j]):
            self.remove(j, x)

    def add(self, component, v):
        self.transactions_[-1].append( ('-', v, component) )
        self.transactions_[-1].append( ('+', v, self.vertices_[v]) )
        self.lists_[component].add(v)
        self.vertices_[v] = component

    def remove(self, component, v):
        self.transactions_[-1].append( ('+', v, component) )
        self.lists_[component].remove(v)

    def start_transaction(self):
        self.transactions_.append([])

    def rollback_transaction(self):
        for t in self.transactions_[-1]:
            if t[0] == '+':
                self.lists_[t[2]].add(t[1])
                self.vertices_[t[1]] = t[2]
            else:
                self.lists_[t[2]].remove(t[1])
        self.transactions_.pop()

    def component(self, v):
        return self.vertices_[v]

    def components(self):
        return self.lists_

if __name__ == "__main__":
    cl = ComponentsList(5)
    cl.start_transaction()
    cl.union(1, 2)
    print('1', cl.components()[1])
    print('1a', cl.components()[2])
    cl.start_transaction()
    cl.union(3, 4)
    print('2', cl.components()[1])
    print('3', cl.components()[3])
    cl.start_transaction()
    cl.union(1, 3)
    print('4', cl.components()[1])
    print('5', cl.components()[3])
    cl.rollback_transaction()
    print('6', cl.components()[1])
    cl.rollback_transaction()
    print('7', cl.components()[1])
    cl.rollback_transaction()
    print('8', cl.components()[1])
