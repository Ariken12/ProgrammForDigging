from Core.Components.Compute.Compute import Compute
from Core.Components.Parser import Parser
from Core.Components.Dumper import Dumper
from Core.Components.Serializer import Serializer


class Core:
    def __init__(self):
        self.clean()

    def clean(self):
        self.clear()
        self.compute = Compute(self)
        self.parser = Parser(self)
        self.dumper = Dumper(self)
        self.serializer = Serializer(self)

    def set(self, *data, **kwdata):
        for key in kwdata:
            if key in ('table', 'namespace', 'parameters', 'plan', 'meta'):
                self.data[key] = kwdata[key]
            if key in ('ore_types', 'component_types', 'places'):
                self.data[key] = tuple([kwdata[key][i] for i in kwdata[key]])
        
    def get_headers(self):
        return self.data['namespace'], self.data['places'], self.data['ore_types'], self.data['component_types']
    
    def __getitem__(self, item):
        return self.data[item]
        
    def __setitem__(self, item, value):
        self.data[item] = value

    def clear(self):
        self.data = {
            'table': [],
            'namespace': '',
            'parameters': {
                'acceleration': (),
                'max_dh': {},
                'components_lim': (),
                'begin_date': (),
                'step_date': (),
                'k_func': (),
                'max_k': (),
                'usefull_ores': {}, 
                'measure_count': {}
            },
            'plan': {},
            'plan_modify': {},
            'meta': {
                'places': {},
                'ores': {},
                'components': {}
            },
            'ore_types': (),
            'component_types': (),
            'places': ()
        }
    
    def recalculate(self):
        self.compute.calculate_places()
