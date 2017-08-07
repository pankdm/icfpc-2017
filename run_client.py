from client import *

from config import create_punter

from fast_greedy_punter import *

if __name__ == "__main__":
    port = int(sys.argv[1])

    punter = create_punter(FastGreedyPunter, splurges_on_claim=True, log=True)

    client = Client(SERVER, port)
    client.run(punter)
