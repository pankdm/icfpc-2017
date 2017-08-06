import express from 'express';
import { createServer } from 'http';
import { Server as WebSocket } from 'ws';
import { createServer as createTcpServer } from 'net';
import winston from 'winston';
import jsonfile from 'jsonfile';
import Engine from './engine';
import WsClient from './wsclient';
import TcpClient from './tcpclient';

const httpPort = process.env.HTTP_PORT || 8888;
const wsPort = process.env.WS_PORT || 9998;
const tcpPort = process.env.TCP_PORT || 9999;

winston.level = process.env.LOG_LEVEL || 'info';

const app = express();
const http = createServer(app);

app.use(express.static('static'));
http.listen(httpPort, () => {
  winston.info(`Listening on ${http.address().port}`);
});

const players = parseInt(process.env.PLAYERS, 10) || 2;
winston.info(`players supported: ${players}`);
const map = jsonfile.readFileSync(`static/maps/${process.env.MAP}.json`);
if (map === null) {
  winston.error('map not found');
  process.exit(-1);
}

const engine = new Engine(map, players);

const wsServer = new WebSocket({ port: wsPort });
wsServer.on('connection', (ws) => {
  winston.info('websocket connected');
  const _ = new WsClient(ws, engine);
});

const tcpServer = createTcpServer((socket) => {
  winston.info('tcp connected');
  const _ = new TcpClient(socket, engine);
});

tcpServer.listen({ port: tcpPort }, () => {
  winston.info(`tcp created at port ${tcpPort}`);
});
