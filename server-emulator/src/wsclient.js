import winston from 'winston';
import Client from './client';

export default class WsClient extends Client {
  constructor(socket, engine) {
    super(socket, engine);
    socket.on('message', (data, _flags) => {
      winston.verbose(`data: ${data}`);
      engine.doMove(Client.fromJson(data));
    });

    socket.on('error', (error) => {
      winston.error(`error: ${error}`);
      engine.shutdown(this);
    });

    socket.on('close', () => {
      winston.info('disconnected');
      engine.shutdown(this);
    });
  }

  send(message) {
    super.send(message);
    this.socket.send(Client.toJson(message));
  }

  disconnect() {
    super.disconnect();
    this.socket.close();
  }
}
