#!/bin/bash
shopt -s expand_aliases

alias ICFPC_MIRROR="wget --mirror -p --convert-links -nH -c"
ROOT="http://punter.inf.ed.ac.uk"

ICFPC_MIRROR "$ROOT/graph-viewer/index.html"
ICFPC_MIRROR "$ROOT/puntfx/index.html"
ICFPC_MIRROR "$ROOT/graph-viewer/maps.json"
jq -r --arg ROOT $ROOT '.maps | .[]? | .filename | $ROOT+"/graph-viewer/"+.' graph-viewer/maps.json | ICFPC_MIRROR -i -

unalias ICFPC_MIRROR
