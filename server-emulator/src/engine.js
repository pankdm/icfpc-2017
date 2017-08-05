import winston from 'winston';
import { Graph, alg, json } from 'graphlib';
import jsonfile from 'jsonfile';
import moment from 'moment';
import mkdirp from 'mkdirp';

export default class Engine {
  constructor(map, players) {
    this.map = map;
    this.players = players;
    this.moves = [];
    this.queue = [];
    this.graphs = [];
    this.clients = [];

    const weightGraph = new Graph({ directed: false });
    this.map.sites.forEach((site) => {
      weightGraph.setNode(`${site.id}`);
    });
    this.map.rivers.forEach((river) => {
      weightGraph.setEdge(`${river.source}`, `${river.target}`);
    });
    this.weights = {};
    this.map.mines.forEach((mine) => {
      this.weights[mine] = alg.dijkstra(weightGraph, `${mine}`, null, v => weightGraph.nodeEdges(v));
    });

    winston.info(`target weights: ${JSON.stringify(this.weights)}`);
  }

  static extractId(move) {
    const action = move.claim || move.pass;
    return action.punter;
  }

  addClient(client) {
    const id = this.clients.length;
    this.clients.push(client);
    client.setId(id);

    if (this.clients.length === this.players) {
      this.beginGame();
    }
  }

  nextMove() {
    const id = Engine.extractId(this.queue[0]);
    const message = {
      move: {
        moves: this.queue,
      },
    };
    this.clients[id].send(message);
    this.queue.shift();
  }

  beginGame() {
    winston.info('begin of game');

    this.clients.forEach((client) => {
      this.queue.push({
        pass: {
          punter: client.id,
        },
      });

      const graph = new Graph({ directed: false });
      this.map.sites.forEach((site) => {
        graph.setNode(`${site.id}`);
      });
      this.graphs.push(graph);

      const message = {
        punter: client.id,
        punters: this.players,
        map: this.map,
      };
      client.send(message);
      winston.verbose(message);
    });

    this.tryMoving();
  }

  endGame() {
    winston.info('end of game');
    const scores = [];

    this.graphs.forEach((graph, id) => {
      winston.info(`${id} graph: ${JSON.stringify(json.write(graph))}`);
      let score = 0;
      this.map.mines.forEach((mine) => {
        const dists = alg.dijkstra(graph, `${mine}`, null, v => graph.nodeEdges(v));
        Object.entries(dists).forEach((entry) => {
          const key = entry[0];
          const value = entry[1];
          if (value && value.distance !== null && value.distance !== Infinity) {
            const dist = this.weights[mine][key].distance;
            score += dist * dist;
          }
        });
      });

      scores.push({
        punter: id,
        score: score,
      });
    });

    winston.info(`scores: ${JSON.stringify(scores)}`);

    while (this.queue.length) {
      const id = Engine.extractId(this.queue[0]);
      const message = {
        stop: {
          moves: this.queue,
          scores: scores,
        },
      };
      this.clients[id].send(message);
      this.queue.shift();
    }
    while (this.clients.length) {
      const client = this.clients.pop();
      client.disconnect();
    }

    const dump = {
      map: this.map,
      players: this.players,
      moves: this.moves,
      scores: scores,
    };
    const log = `logs/${moment().format()}.json`.replace(/:/g, '');
    mkdirp('logs', (err) => {
      if (err) {
        winston.error(err);
        this.graphs.length = 0;
        this.moves.length = 0;
      } else {
        jsonfile.writeFile(log, dump, { spaces: 2 }, (innerr) => {
          if (innerr) {
            winston.error(innerr);
          } else {
            winston.info(`log file ${log} has been saved!`);
          }
          this.graphs.length = 0;
          this.moves.length = 0;
        });
      }
    });
  }

  doMove(move) {
    const action = move.claim || move.pass;
    if (action) {
      const resultMove = move;
      if (move.claim) {
        const claimedRiver = this.map.rivers.find(river =>
          (river.source === move.claim.source && river.target === move.claim.target)
            || (river.source === move.claim.target && river.target === move.claim.source));

        resultMove.claim.source = claimedRiver.source;
        resultMove.claim.target = claimedRiver.target;

        const id = move.claim.punter;
        this.graphs[id].setEdge(`${move.claim.source}`, `${move.claim.target}`);
      }

      this.queue.push(resultMove);
      this.moves.push(resultMove);

      if (this.moves.length < this.map.rivers.length) {
        this.nextMove();
      } else {
        this.endGame();
      }
    }
  }

  shutdown(client) {
    this.clients.splice(this.clients.indexOf(client), 1);
  }

  tryMoving() {
    winston.info('tryMoving');
    let ready = true;
    this.clients.forEach((client) => {
      winston.info(`${client.id} ready: ${client.isReady()}`);
      if (client.isReady() !== true) {
        ready = false;
      }
    });
    if (ready) {
      this.nextMove();
    }
  }
}
