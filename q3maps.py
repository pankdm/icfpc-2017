from copy import deepcopy
import random

def m(map_name, **kwargs):
    return ("maps/{}".format(map_name), kwargs)


MAPS = [
    m("sample.json", n=2),

    m("lambda.json", n=4),
    m("circle.json", n=4),
    m("Sierpinski-triangle.json", n=3),

    m("Sierpinski-triangle3.json", n=3), # disjoint map

    m("tube.json", n=8),
    m("randomMedium.json", n=8),
    m("randomSparse.json", n=8),
    m("boston-sparse.json", n=8),
]

BIG_MAPS = [
    m("edinburgh-sparse.json", n=16),
    m("gothenburg-sparse.json", n=16),
    m("nara-sparse.json", n=16),
    m("oxford-center-sparse.json", n=16),
    m("oxford2-sparse-2.json", n=16),
    m("van-city-sparse.json", n=16),
]

ORIGINAL_MAPS = MAPS + BIG_MAPS

random.shuffle(BIG_MAPS)
MAPS.extend(BIG_MAPS)
