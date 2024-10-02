
from typing import Any


struct = {
            'table': [],
            'name_space': '',
            'horizont_size': 0,
            'max_horizont': 0,
            'ore_types': []
        }

class Data:
    def __init__(self):
        self.clear()

    def get_meta(self):
        return self.name_space, self.places, self.ore_types

    def set(self, *args, **kwargs):
        if 'table' in kwargs:
            self.table = kwargs['table']
        if 'name_space' in kwargs:
            self.name_space = kwargs['name_space']
        if 'ore_types' in kwargs:
            self.ore_types = kwargs['ore_types']
        if 'component_types' in kwargs:
            self.components_types = kwargs['component_types']
        if 'places' in kwargs:
            for place in kwargs['places']:
                self.places[place] = []
                for row in self.table:
                    if row[0] == place:
                        self.places[place].append(row[1:])
        if 'dates' in kwargs:
            for date in kwargs['dates']:
                self.plan[date] = {}
                for place in kwargs['dates'][date]:
                    self.plan[date][place] = []
                    for row in kwargs['dates'][date][place]:
                        self.plan[date][place].append(row)
        if 'resources' in kwargs:
            resources = kwargs['resources']
            for date in resources:
                if date not in self.resources_for_plan:
                    self.resources_for_plan[date] = {}
                    self.components[date] = {}
                for place in resources[date]:
                    self.resources_for_plan[date][place] = resources[date][place]
                    self.components[date][place] = []
        if 'parameters' in kwargs:
            for key in kwargs['parameters']:
                self.parameters[key] = kwargs['parameters'][key]

    def __getitem__(self, key):
        if key in self.places:
            return self.places[key]
        if key in self.plan:
            return self.plan[key]
        
    def clear_dates(self):
        for date in self.plan:
            for place in self.plan[date]:
                self.plan[date][place] = []

    def clear_resources(self):
        pass

    def clear(self):
        self.table = []
        self.name_space = ''
        self.ore_types = []
        self.horizont_size = 0
        self.max_horizont = 0
        self.data = None
        self.components_types = []
        '''("component1", "component2", "component3", ...)'''
        self.places = []
        '''("place1", "place2", "place3", ...)'''
        self.components = {'date': {'place': ['component1', ...]}}
        '''{'date': {'place': ['component1', ...]}}'''
        self.resources_for_plan = {'date': {'place': ['ore_1', 'ore_2']}}
        self.plan = {'date': {'place': [('horizonts', 'ores'), ...]}}
        self.parameters = {}
        self.meta = {
            'places': {

            },
            'components': {

            },
            'ores': {
                
            }
        }
