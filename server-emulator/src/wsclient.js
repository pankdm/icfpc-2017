import winston from 'winston';
import Client from './client';

export default class WsClient extends Client {
  constructor(socket, engine) {
    super(socket, engine);
    socket.on('message', (data, _flags) => {
      winston.verbose(`data: ${data}`);
      const msg = Client.fromJson(data.toString());

      if (msg.me !== undefined) {
        winston.verbose('handshake');
        this.engine.addClient(this, msg.me);
      } else if (msg.claim !== undefined || msg.pass !== undefined) {
        this.engine.doMove(msg);
      }
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
