from union_find import ComponentsList



def test7():
    cl = ComponentsList(8)
    cl.start_transaction()
    cl.union(0, 7)
    cl.union(7, 1)
    print('c 0', cl.components()[0])
    print('c 1', cl.components()[1])
    print('c 7', cl.components()[7])

test7()
