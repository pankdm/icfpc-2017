import cPickle
import base64

class OfflinePunter:
    def get_state(self):
        pass

    def set_state(self, state_tuple):
        pass

    def get_state_for_write(self):
        state = self.get_state()
        pickled_state = cPickle.pickle(state)
        return base64.b64encode(pickled_state)

    def set_state_from_written(self, encoded_state):
        pickled_state = base64.b64decode(encoded_state)
        state = cPickle.unpickle(pickled_state)
        self.set_state(state)

    def run(self, input_json):
        if "state" in input_json:
            self.set_state_from_written(input_json["state"])
        if "punter" in input_json:
            res = self.process_setup(input_json)
        else:
            res = self.process_move(input_json)
        if not "stop" in input_json:
            res["state"] = self.get_state_for_write()
        return res
