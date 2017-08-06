import winston from 'winston';
import Client from './client';

export default class TcpClient extends Client {
  constructor(socket, engine) {
    super(socket, engine);
    this.ready = false;
    winston.info(`new client connection from ${socket.remoteAddress}:${socket.remotePort}`);
    socket.setEncoding('utf8');
    socket.on('data', (data, _flags) => {
      winston.verbose(`data: ${data}`);
      const msg = Client.fromJson(data.toString());

      if (msg.me !== undefined) {
        winston.verbose('handshake');
        this.send({
          you: msg.me,
        });
        this.engine.addClient(this, msg.me);
      } else if (msg.ready !== undefined) {
        this.ready = true;
        this.engine.tryMoving();
      } else if (msg.claim !== undefined || msg.pass !== undefined) {
        this.engine.doMove(msg);
      }
    });

    socket.on('error', (error) => {
      winston.error(`error: ${error}`);
      this.engine.shutdown(this);
    });

    socket.on('end', () => {
      winston.info('disconnected');
      this.engine.shutdown(this);
    });
  }

  send(message) {
    super.send(message);
    this.socket.write(Client.toJson(message));
  }

  disconnect() {
    super.disconnect();
    this.socket.end();
  }
}
