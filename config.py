

def create_punter(cls, log=False, name=""):
    c = Config()
    c.log = log
    c.name = name
    return cls(c)

class Config:
    def __init__(self):
        self.log = False
        self.name = ""
