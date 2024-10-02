from Core.Components.Data import Data
from Core.Components.Compute import Compute
from Core.Components.Parser import Parser
from Core.Components.Dumper import Dumper
from Core.Components.Serializer import Serializer

class Core:
    def __init__(self):
        self.data = Data()
        self.compute = Compute(self)
        self.parser = Parser(self)
        self.dumper = Dumper(self)
        self.serialize = Serializer(self)

    def clean(self):
        self.data = Data()
        self.compute = Compute(self)
        self.parser = Parser(self)

    def set(self, *data, **kwdata):
        self.data.set(*data, **kwdata)

    def data_get_meta(self):
        return self.data.get_meta()
    
    def __getitem__(self, item):
        return self.data[item]
    
    def recalculate(self):
        self.compute.calculate_places()

    def start(self):
        process = self.compute.main_calculate()
        while (output := next(process)) != None:
            yield output
        while True:
            yield None