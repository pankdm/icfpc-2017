import winston from 'winston';

export default class Client {
  constructor(socket, engine) {
    this.socket = socket;
    this.engine = engine;
    this.ready = true;
  }

  setId(value) {
    this.id = value;
  }

  send(message) {
    winston.verbose(`send ${JSON.stringify(message)}`);
  }

  disconnect() {
    winston.info(`disconnect client ${this.id}`);
  }

  static fromJson(data) {
    try {
      return JSON.parse(data.split(/:(.+)/)[1]);
    } catch (e) {
      winston.debug(e);
      return {};
    }
  }

  static toJson(body) {
    const textBody = JSON.stringify(body);
    return `${textBody.length}:${textBody}`;
  }

  isReady() {
    return this.ready;
  }
}
