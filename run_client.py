from client import *

from config import create_punter

from all_solvers import *

if __name__ == "__main__":
    port = int(sys.argv[1])

    # punter = create_punter(FastGreedyPunter, splurges_on_claim=True, log=True)
    punter = create_punter(FastGreedyOptions, log=True)

    client = Client(SERVER, port)
    client.run(punter)
