from union_find import ComponentsList



def test7():
    cl = ComponentsList(8)
    cl.start_transaction()
    cl.union(0, 7)
    cl.union(0, 1)
    print('c 0', cl.components()[cl.component(0)])
    print('c 1', cl.components()[cl.component(1)])
    print('c 7', cl.components()[cl.component(7)])
    cl.rollback_transaction()
    print('c 0', cl.components()[cl.component(0)])
    print('c 1', cl.components()[cl.component(1)])
    print('c 7', cl.components()[cl.component(7)])

test7()
