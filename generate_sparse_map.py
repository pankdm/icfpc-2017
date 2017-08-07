import json
import sys
import pprint
import copy
import random

filename_in = sys.argv[1]
filename_out = sys.argv[2]

with open(filename_in) as data_in:
    jIn = json.loads(data_in.read())

remap = {}
used = set()

def gen_id(v):
    if v in remap:
        return

    r = random.randint(0, 10000000000)
    while r in used:
        r = random.randint(0, 10000000000)

    remap[v] = r

for r in jIn["rivers"]:
    s = int(r["source"])
    f = int(r["target"])
    gen_id(s)
    gen_id(f)

jOut = {"rivers": [], "mines": [], "sites": []}

for r in jIn["rivers"]:
    s = r["source"]
    f = r["target"]
    jOut["rivers"].append( {"source": remap[s], "target": remap[f]} )
for m in jIn["mines"]:
    jOut["mines"].append(remap[m])
for s in jIn["sites"]:
    sId = s["id"]
    sX = s["x"]
    sY = s["y"]
    jOut["sites"].append( {"id": remap[sId], "x": sX, "y": sY} )

# pprint.pprint(jOut)

with open(filename_out, "w") as data_out:
    json.dump(jOut, data_out)
