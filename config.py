

def create_punter(cls, log=False):
    c = Config()
    if log:
        c.log = True
    return cls(c)

class Config:
    def __init__(self):
        self.log = False
