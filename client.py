from __future__ import print_function


from chaos_punter import ChaosPunter
from greedy_punter import GreedyPunter

from config import Config

import socket
import sys
import json
import pprint


SERVER = "punter.inf.ed.ac.uk"
BUFFER_SIZE = 1024

class Client:
    def __init__(self, port):
        self.port = port
        self.inner_buffer = ""

    def send_message(self, data):
        message = json.dumps(data)
        n = len(message)
        tcp_msg = "{}:{}".format(n, message)
        print('sending {}'.format(tcp_msg))
        self.s.send(tcp_msg.encode())

    def read_message(self):
        # read size first
        buffer = self.inner_buffer
        while True:
            data = self.s.recv(BUFFER_SIZE)
            buffer += data.decode()
            index = buffer.find(":")
            if index != -1:
                expected_size = int(buffer[0 : index])
                # print 'Will read {} bytes'.format(expected_size)
                buffer = buffer[index + 1:]
                break

        # read the rest of the message
        while len(buffer) < expected_size:
            data = self.s.recv(BUFFER_SIZE)
            buffer += data.decode()

        self.inner_buffer = buffer[expected_size:]
        buffer = buffer[:expected_size]

        # print 'parsing json: {}'.format(buffer)
        js = json.loads(buffer)

        # print('got message:')
        # pprint.pprint(js)
        return js


    def run(self, punter):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((SERVER, self.port))

        # handshake
        data = punter.get_handshake()
        self.send_message(data)
        js = self.read_message()

        # setup message
        print('Waiting on setup')
        setup_msg = self.read_message()
        reply = punter.process_setup(setup_msg)
        self.send_message(reply)

        # now playing
        while True:
            move_msg = self.read_message()
            reply = punter.process_move(move_msg)
            if reply == None:
                break
            self.send_message(reply)



if __name__ == "__main__":
    port = int(sys.argv[1])
    config = Config()
    config.log = True

    # punter = ChaosPunter(config)
    punter = GreedyPunter(config)

    client = Client(port)
    client.run(punter)
