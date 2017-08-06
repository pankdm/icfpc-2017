

def create_punter(cls, **kwargs):
    c = Config()
    for k, v in kwargs.items():
        setattr(c, k, v)
    return cls(c)

class Config:
    def __init__(self):
        self.log = False
        self.name = ""
        self.futures = False
