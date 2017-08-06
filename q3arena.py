from q3robots import *
from server import *
from config import *

from chaos_punter import ChaosPunter


import random
import os
import q3maps
import json
import string
import time
import uuid

def random_string(N):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(N))

SETTINGS = [
    # {},
    {"futures": True},
]

def select_punters(size):
    all_punters = create_all_robots()
    indexes = range(len(all_punters))
    punters = []
    if len(all_punters) < size:
        punters = all_punters
        while len(punters) < size:
            punters.append( create_punter(ChaosPunter) )
    else:
        selected_indexes = random.sample(indexes, size)
        for i in selected_indexes:
            punters.append(all_punters[i])

    random.shuffle(punters)
    return punters

class Q3Arena:
    def __init__(self):
        self.round = 0
        # validate all maps exist
        for m, other in q3maps.MAPS:
            assert os.path.isfile(m)

    def write_data(self, data, webserver_data):
        loc = 'arena/results'
        files = os.listdir(loc)
        latest = 0
        for f in files:
            if f.endswith(".json"):
                start = f.split('-')[0]
                if start.isdigit():
                    latest = max(latest, int(start))

        # write result logs
        ff = '{:07d}-{}.json'.format(latest + 1, random_string(4))
        fname = '{}/{}'.format(loc, ff)
        js_data = json.dumps(data)
        print 'File {}: writing {}'.format(fname, js_data)
        f = open(fname, 'wt')
        json.dump(js_data, f)
        f.close()

        # write webserver logs
        g = open('arena/battle_logs/{}'.format(ff), 'wt')
        json.dump(webserver_data, g)
        g.close()


    def _run_round(self, map_file, map_settings, settings):
        n = map_settings["n"]
        battle_id = uuid.uuid4()

        print ''
        print 'Starting round {} on map {}, n={}'.format(self.round, map_file, n)

        punters = select_punters(size=n)
        # print 'Players:'
        # for i, p in enumerate(punters):
        #     print '{}: {}'.format(i, p.get_handshake()["me"])

        config = Config()
        config.log = False

        s = Server(punters, map_file, settings, config=config)
        s.run()
        webserver_data = s.get_logs_to_dump()
        for result in s.results_to_log:
            print result

        data = {
            "map": map_file,
            "map_settings": map_settings,
            "settings": settings,
            "results": s.results_to_log,
            "ts": int(time.time()),
            # "battle_id": str(battle_id),
        }
        self.write_data(data, webserver_data)

    def run_forever(self):
        self.round = 0
        while True:
            for settings in SETTINGS:
                for m, m_settings in q3maps.MAPS:
                    self.round += 1
                    self._run_round(m, m_settings, settings)

def run():
    q3 = Q3Arena()
    q3.run_forever()


if __name__ == "__main__":
    os.system("mkdir -p arena/results")
    os.system("mkdir -p arena/battle_logs")

    run()
