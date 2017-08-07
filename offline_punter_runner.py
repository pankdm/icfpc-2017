#!/usr/bin/env python
import sys
import json

from fast_greedy_stochastic_punter import FastGreedyStochasticPunter, FastGreedyStochasticMaxPunter, FastGreedyStochasticBridgesMaxPunter, FastGreedyStochasticBridgesVerticesMaxPunter

from config import create_punter, Config

log = True

if log:
    fLog = open("log", "w")

def read(k):
    res = sys.stdin.read(k)
    if log:
        print >>fLog, "read: %d %s" % (k, str(res))
    return res

def readInputJson():
    sLen = ""
    ch = read(1)
    while ch != ':':
        sLen += ch
        ch = read(1)
    ln = int(sLen)
    mgs = read(ln)
    return json.load(msg)

def writeOutputJson(obj):
    jsonOut = json.dumps(obj)
    res = str(len(jsonOut)) + ":" + jsonOut
    sys.stdout.write(res)
    sys.stdout.flush()

import traceback

def log_traceback(ex, ex_traceback=None):
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [ line.rstrip('\n') for line in traceback.format_exception(ex.__class__, ex, ex_traceback)]
    exception_logger.log(tb_lines)

if __name__ == "__main__":
    try:
        punter = create_punter(FastGreedyStochasticBridgesVerticesMaxPunter, log=False, name="FastGreedyStochasticBridgesVerticesMaxPunter 1")
        hs = punter.get_handshake()
        writeOutputJson(hs)
        ack = readInputJson()
        inp = readInputJson()
        out = punter.run(inp)
        writeOutputJson(out)
    except ex:
        if log:
            print >>fLog, str(ex)
            _, _, ex_traceback = sys.exc_info()
            log_traceback(ex, ex_traceback)
        sys.exit(1)
