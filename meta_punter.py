import offline_punter
import vlad_solver2
import fast_greedy_options
from config import create_punter

class MetaPunter(offline_punter.OfflinePunter):
    def __init__(self, config):
        self.name = "greedy monkey" if not config.name else config.name
        self.config = config
        self.fast = create_punter(fast_greedy_options.FastGreedyOptions, log=False, name=self.name)
        self.vlad = create_punter(vlad_solver2.VladSolver2, log=False, name=self.name)
        self.size = 0

    def get_handshake(self):
        return {"me": self.name}

    def get_state(self):
        old = self.get_punter().get_state()
        old.insert(0, self.size)
        return old

    def set_state(self, state_tuple):
        self.size = state_tuple[0]
        self.get_punter().set_state(state_tuple[1:])

    def run(self, input_json):
        if "punter" in input_json:
            vertices = set()
            for river in input_json["map"]["rivers"]:
                vertices.add(river["source"])
                vertices.add(river["target"])
            self.size = len(vertices)
        return self.get_punter().run(input_json)

    def get_punter(self):
        if self.size < 97:
            return self.vlad
        else:
            return self.fast
    
    def process_setup(self, data):
        return self.get_punter().process_setup(data)
    
    def process_move(self, data):
        return self.get_punter().process_move(data)
