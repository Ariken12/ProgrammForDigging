

class Parser:
    def __init__(self, core):
        self.core = core

    def __call__(self, filename):
        self.data = self.core.data
        