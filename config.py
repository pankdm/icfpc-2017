

def create_punter(cls, log=False, name="", futures=False):
    c = Config()
    c.log = log
    c.name = name
    c.futures = futures
    return cls(c)

class Config:
    def __init__(self):
        self.log = False
        self.name = ""
        self.futures = False
