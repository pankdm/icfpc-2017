import json
import sys
import pprint
import copy

filename_in = sys.argv[1]
filename_out = sys.argv[2]

with open(filename_in) as data_in:
    jIn = json.loads(data_in.read())

n = 0
for r in jIn["rivers"]:
    s = int(r["source"])
    f = int(r["target"])
    n = max(n, s)
    n = max(n, f)
n += 1

jOut = copy.deepcopy(jIn)

def add(offset, offset_x, offset_y):
    for r in jIn["rivers"]:
        s = r["source"]
        f = r["target"]
        jOut["rivers"].append( {"source": s + offset, "target": f + offset} )
    for m in jIn["mines"]:
        jOut["mines"].append(m + offset)
    for s in jIn["sites"]:
        sId = s["id"]
        sX = s["x"]
        sY = s["y"]
        jOut["sites"].append( {"id": sId + offset, "x": sX + offset_x, "y": sY + offset_y} )

add(n, 10, 0)
add(2*n, 0, 10)

# pprint.pprint(jOut)

with open(filename_out, "w") as data_out:
    json.dump(jOut, data_out)
