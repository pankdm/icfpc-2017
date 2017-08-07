#!/usr/bin/env python
import sys
import json
import os

# from fast_greedy_stochastic_punter import FastGreedyStochasticPunter, FastGreedyStochasticMaxPunter, FastGreedyStochasticBridgesMaxPunter, FastGreedyStochasticBridgesVerticesMaxPunter
from fast_greedy_options import FastGreedyOptions

from config import create_punter, Config

log = len(sys.argv) == 1

def next_name(prefix):
    index = 0
    while os.path.isfile(prefix + str(index)):
        index += 1
    return prefix + str(index)

if log:
    fLog = open(next_name("log"), "w")

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
    msg = read(ln)
    return json.loads(msg)

def writeOutputJson(obj):
    jsonOut = json.dumps(obj)
    res = str(len(jsonOut)) + ":" + jsonOut
    if log:
        print >>fLog, "write: %s" % res
    sys.stdout.write(res)
    sys.stdout.flush()

import traceback

def log_traceback(ex, ex_traceback=None):
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [ line.rstrip('\n') for line in traceback.format_exception(ex.__class__, ex, ex_traceback)]
    if log:
        print >>fLog, tb_lines

if __name__ == "__main__":
    try:
        punter = create_punter(FastGreedyOptions, log=False, name="LinearMaxCappedFlowWithBridgesAndLogLossRegression")
        hs = punter.get_handshake()
        writeOutputJson(hs)
        ack = readInputJson()
        inp = readInputJson()
        out = punter.run(inp)
        if out:
            writeOutputJson(out)
        else:
            if log:
                if "stop" in inp:
                    if "scores" in inp["stop"]:
                        print >>fLog, "me: %d" % punter.punter_id, inp["stop"]["scores"]
        if log:
            fLog.flush()
    except Exception as ex:
        if log:
            print >>fLog, "Exception:", str(ex)
            _, _, ex_traceback = sys.exc_info()
            log_traceback(ex, ex_traceback)
        sys.exit(1)
