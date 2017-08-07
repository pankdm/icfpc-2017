#!/usr/bin/env python
import sys
import json

from fast_greedy_stochastic_punter import FastGreedyStochasticPunter, FastGreedyStochasticMaxPunter, FastGreedyStochasticBridgesMaxPunter, FastGreedyStochasticBridgesVerticesMaxPunter

from config import create_punter, Config

def readInputJson():
    sLen = ""
    ch = sys.stdin.read(1)
    while ch != ':':
        sLen += ch
        ch = sys.stdin.read(1)
    ln = int(sLen)
    mgs = sys.stdin.read(ln)
    return json.load(msg)

def writeOutputJson(obj):
    jsonOut = json.dumps(obj)
    res = str(len(jsonOut)) + ":" + jsonOut
    sys.stdout.write(res)

if __name__ == "__main__":
    punter = create_punter(FastGreedyStochasticBridgesVerticesMaxPunter, log=False, name="FastGreedyStochasticBridgesVerticesMaxPunter 1")
    hs = punter.get_handshake()
    writeOutputJson(hs)
    ack = readInputJson()
    inp = readInputJson()
    out = punter.run(inp)
    writeOutputJson(out)
