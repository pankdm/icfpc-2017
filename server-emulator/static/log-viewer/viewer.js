/* GLOBALS */
let punterID = -1;
let numPunters = -1;
let initialised = false;

let queuedClaims = [];
let queuedPass = false;

let logfile = {};
let logmove = 0;
let timerId = -1;
let log;

const hostname = "127.0.0.1";
const relayPort = 9998;

/* Graph rendering */

const colours =
  ["#1f77b4",
   "#aec7e8",
   "#ff7f0e",
   "#ffbb78",
   "#2ca02c",
   "#98df8a",
   "#d62728",
   "#ff9896",
   "#9467bd",
   "#c5b0d5",
   "#8c564b",
   "#c49c94",
   "#e377c2",
   "#f7b6d2",
   "#7f7f7f",
   "#c7c7c7",
   "#bcbd22",
   "#dbdb8d",
   "#17becf",
   "#9edae5"];

function getPunterColour(punter) {
  return colours[punter % colours.length];
}

function renderGraph(graph) {
    initCy(graph,
           function() {
               initialised = true;
               cy.autolock(true);
               bindCoreHandlers();
               if (queuedClaims.length > 0 || queuedPass) {
                   playQueuedClaims();
                   ourTurn();
               } else {
                   theirTurn();
               }
           }
          );
    return;
}

function toggleButton(buttonId, st) {
  $("#" + buttonId).attr("disabled", st);
}

function disableButton(buttonId) {
  toggleButton(buttonId, true);
}

function enableButton(buttonId) {
  toggleButton(buttonId, false);
}


$(function() {
  $(document).ready(function() {
    enableButton('connect');
    $("#speed").on('slide', setSpeed);
    log = $("#log");
  });
});


/**
 * Communication
 */
function _connect() {
  disableButton('connect');
  enableButton('disconnect');
  const gamePort = $('#gamePort').val();
  const punterName = $('#punterName').val();
  connect(gamePort, punterName);
  return;
}

function _disconnect() {
  disableButton('disconnect');
  enableButton('connect');
  disconnect();
  return;
}

let socket = undefined;

function setStatus(status) {
  $("#game-status").text(status);
}

function clearLog() {
  log.val("");
}

function writeLog(msg) {
    log.val(log.val() + msg + "\n");
    log.scrollTop(log.prop('scrollHeight'));
    return;
}

function deleteLog(msg) {
    let index = log.val().indexOf(msg);
    if (index !== -1) {
      log.val(log.val().substring(0, index));
    }
    log.scrollTop(log.prop('scrollHeight'));
    return;
}

function logInfo(msg) {
    writeLog("info: " + msg);
    return;
}

function logClaim(claim) {
    writeLog("move: punter #" + claim.punter + " claimed edge " +
             claim.source + " -- " + claim.target + ".");
    return;
}

function logPass(pass) {
    writeLog("pass: punter #" + pass.punter + ".");
    return;
}

function deleteClaim(claim) {
    deleteLog("move: punter #" + claim.punter + " claimed edge " +
             claim.source + " -- " + claim.target + ".");
    return;
}

function deletePass(pass) {
    deleteLog("pass: punter #" + pass.punter + ".");
    return;
}

function logScore(punter_id, score) {
  writeLog("punter #" + punter_id + " scored " + score);
}

function logMove(move) {
  if (move.claim !== undefined) {
    logClaim(move.claim);
  } else if (move.pass !== undefined) {
    logPass(move.pass);
  }
}

function deleteMove(move) {
  if (move.claim !== undefined) {
    deleteClaim(move.claim);
  } else if (move.pass !== undefined) {
    deletePass(move.pass);
  }
}

function logError(msg) {
    writeLog("error: " + msg);
    return;
}

function logRelay(msg) {
    writeLog("relay: " + msg);
    return;
}

function connect(gamePort, punterName) {
    let graph = undefined;
    let ws_uri = "ws://" + hostname + ":" + relayPort;
    logInfo("connecting to relay [" + ws_uri + "]...");

    socket = new WebSocket(ws_uri);

    socket.onopen = function(data) {
        logInfo("connection established.");
        setStatus("Connected; waiting for other punters...");
        socket.send(hostname + ":" + gamePort + ":" + punterName);
        return;
    };

    socket.onclose = function(data) {
        logInfo("connection closed by relay.");
        enableButton('connect');
        disableButton('disconnect');
        return;
    }

    socket.onerror = function(err) {
        if (socket.readyState === 3) {
            logError("connection failed.");
        } else {
            logError("connection failure.");
        }
        return;
    };

    socket.onmessage = function(message) {
        try {
            let msg = JSON.parse(message.data.split(/:(.+)/)[1]);
            // Initial message
            if (msg.map !== undefined) {
                // Record our ID, and the number of punters
                punterID = msg.punter;
                numPunters = msg.punters;

                logInfo("our punter ID: " + punterID);
                logInfo("number of punters: " + numPunters);
                logInfo("received initial game graph: " + JSON.stringify(msg.map));
                graph = { "nodes": msg.map.sites,
                          "edges": msg.map.rivers,
                          "mines": msg.map.mines };
                logInfo("rendering game graph...");
                renderGraph(msg.map);
            } else if (msg.move !== undefined) {
                handleIncomingMoves(msg.move.moves);
            } else if (msg.stop !== undefined) {
                handleIncomingMoves(msg.stop.moves);
                printFinalScores(msg.stop.scores);
            } else {
                logError("unknown JSON message: " + message.data);
            }
        } catch (e) { // other message from the server
            console.log(e);
            if (message.data.constructor == String) {
                logRelay(message.data);
            } else {
                logError("received unknown message from relay.");
            }
        }
        return;
    };
    return;
}

function disconnect() {
    socket.close();
    logInfo("disconnected.");
    socket = undefined;
    graph = undefined;
    return;
}

function send(json) {
  const str = JSON.stringify(json);
  socket.send(str.length + ":" + str);
}

function sendClaim(source, target) {
  const req = {
    claim: {
      punter: punterID,
      source: source,
      target: target
    }
  };

  send(req);
}

function sendPass() {
  const req = {
    pass: { punter: punterID }
  };

  send(req);
}

/* EVENT HANDLING LOGIC */

function handleEdgeClick(edge) {
  const source = edge.data("source");
  const target = edge.data("target");

  console.log("edge data; " + edge.data("owner"));
  if (edge.data("owner") == undefined) {
    sendClaim(parseInt(source), parseInt(target));
    cy.edges().unselect();
    updateEdgeOwner(punterID, source, target);
    theirTurn();
  } else {
    logError("That edge is already claimed! (" + source + " -- " + target + ")");
  }
}

function handlePass() {
  sendPass();
  writeLog("Passed!");
  theirTurn();
}

function bindCoreHandlers() {
  cy.edges().on("mouseover", function(evt) {
    this.style("content", this.data("owner"));
  });
  cy.edges().on("mouseout", function(evt) {
    this.style("content", "");
  });
}

function bindOurTurnHandlers() {
  cy.edges().off("select");
  cy.edges().on("select", function(evt) { handleEdgeClick(this) } );
  $("#pass-button").removeAttr("disabled");
}

function bindTheirTurnHandlers() {
  cy.edges().off("select");
  cy.edges().on("select", function(evt) {
    logError("Can't select an edge when it's not your turn to move!");
    cy.edges().unselect();
  } );
  $("#pass-button").attr("disabled", true);
}

function ourTurn() {
  bindOurTurnHandlers();
  setStatus("Your move!");
}

function theirTurn() {
  bindTheirTurnHandlers();
  setStatus("Waiting for others to make a move...");
}


/* GAME UPDATE LOGIC */

function updateEdgeOwner(punter, source, target) {
  const es = cy.edges("[source=\"" + source + "\"][target=\"" + target + "\"]");
  const rs = cy.edges("[source=\"" + target + "\"][target=\"" + source + "\"]");
  if (es.length > 0) {
    const e = es[0];
    e.data()["owner"] = punter;
    e.style("line-color", getPunterColour(punter));
  } else if (rs.length > 0) {
    const e = rs[0];
    e.data()["owner"] = punter;
    e.style("line-color", getPunterColour(punter));
  } else {
    logError("Trying to update nonexistent edge! (" + source + " -- " + target + ")");
  }
}

function resetEdgeOwner(source, target) {
  const es = cy.edges("[source=\"" + source + "\"][target=\"" + target + "\"]");
  const rs = cy.edges("[source=\"" + target + "\"][target=\"" + source + "\"]");
  if (es.length > 0) {
    const e = es[0];
    e.data()["owner"] = null;
    e.style("line-color", "#000099");
  } else if (rs.length > 0) {
    const e = rs[0];
    e.data()["owner"] = null;
    e.style("line-color", "#000099");
  } else {
    logError("Trying to reset nonexistent edge! (" + source + " -- " + target + ")");
  }
}

function printFinalScores(scores) {
  logInfo("Game finished!");
  for (let i = 0; i < scores.length; i++) {
    logScore(scores[i].punter, scores[i].score);
  }
}

function handleIncomingMoves(moves) {
  for (let i = 0; i < moves.length; i++) {
    handleIncomingMove(moves[i]);
  }

  if (initialised) {
    ourTurn();
  }
}

function handleIncomingMove(move) {
  logMove(move);
  if (move.claim !== undefined) {
    const claim = move.claim;
    if (initialised) {
      updateEdgeOwner(claim.punter, claim.source, claim.target);
    } else {
      queueClaim(claim);
    }
  } else if (move.pass !== undefined) {
    if (!initialised) {
      queuedPass = true;
    }
  }
}

function rollbackIncomingMove(move) {
  deleteMove(move);
  if (move.claim !== undefined) {
    const claim = move.claim;
    if (initialised) {
      resetEdgeOwner(claim.source, claim.target);
    } else {
      let popped;
      do {
        popped = queuedClaims.pop();
      } while (popped !== move);
    }
  } else if (move.pass !== undefined) {
    if (!initialised) {
      queuedPass = false;
    }
  }
}

function queueClaim(claim) {
  queuedClaims.push(claim);
}

function playQueuedClaims() {
  for (let i = 0; i < queuedClaims.length; i++) {
    const claim = queuedClaims[i];
    updateEdgeOwner(claim.punter, claim.source, claim.target);
  }
  queuedClaims = [];
  queuedPass = false;
  ourTurn();
}

function updatePlayerControls() {
  toggleButton('next', logmove === logfile.moves.length);
  toggleButton('prev', logmove === 0);

  toggleButton('begin', logmove === 0);
  toggleButton('end', logmove === logfile.moves.length);

  toggleButton('playstop', logmove === logfile.moves.length);
  $("#playstop").text(timerId === -1 ? '|>' : '||');

  $("#current-move").text("Move #" + logmove);
}

function doMove() {
  handleIncomingMove(logfile.moves[logmove++]);

  if (logmove === logfile.moves.length) {
    stop();
    printFinalScores(logfile.scores);
  }

  updatePlayerControls();
}

function undoMove() {
  rollbackIncomingMove(logfile.moves[--logmove]);

  updatePlayerControls();
}

function playstop() {
  if (timerId === -1) {
    play();
  } else {
    stop();
  }
}

function play() {
  stop();
  timerId = setInterval(doMove, $("#speed").slider('getValue'));
}

function stop() {
  if (timerId !== -1) {
    clearInterval(timerId);
    timerId = -1;
  }
}

function begin() {
  stop();
  while (logmove !== 0) {
    undoMove();
  }
  updatePlayerControls();
}

function end() {
  stop();
  while (logmove !== logfile.moves.length) {
    doMove();
  }
}

function setSpeed() {
  if (timerId !== -1) {
    play();
  }
}

function readLogFile(input) {
  stop();
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const data = e.target.result;
      logfile = JSON.parse(data);
      $("#punters").text(logfile.players.length);
      let names = "";
      for (let i = 0; i < logfile.players.length; i++) {
        names += "punter #" + logfile.players[i].id + " — " + logfile.players[i].name + "\n";
      }
      $("#names").val(names);
      $("#moves").text(logfile.moves.length);

      renderGraph(logfile.map);
      begin();
    }
    reader.readAsText(input.files[0]);
  }
}
