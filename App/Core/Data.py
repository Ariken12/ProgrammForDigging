
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
        self.table = []
        self.name_space = ''
        self.ore_types = []
        self.data = None
        self.places_with_all = {}
        self.components = {'date': {'place': ['component1', ...]}}
        self.dates_for_plan = {'date': {'place': [('horizonts', 'ores'), ...]}}
        self.resources_for_plan = {'date': {'place': ['ore_1', 'ore_2']}}

    def get_meta(self):
        return self.name_space, self.places_with_all, self.ore_types

    def set(self, *args, **kwargs):
        if 'table' in kwargs:
            self.table = kwargs['table']
        if 'name_space' in kwargs:
            self.name_space = kwargs['name_space']
        if 'ore_types' in kwargs:
            self.ore_types = kwargs['ore_types']
        if 'places' in kwargs:
            for place in kwargs['places']:
                self.places_with_all[place] = []
                for row in self.table:
                    if row[0] == place:
                        self.places_with_all[place].append(row[1:])
        if 'dates' in kwargs:
            for date in kwargs['dates']:
                self.dates_for_plan[date] = {}
                for place in kwargs['dates'][date]:
                    self.dates_for_plan[date][place] = []
                    for row in kwargs['dates'][date][place]:
                        self.dates_for_plan[date][place].append(row)
        if 'resources' in kwargs:
            resources = kwargs['resources']
            for date in resources:
                if date not in self.resources_for_plan:
                    self.resources_for_plan[date] = {}
                    self.components[date] = {}
                for place in resources[date]:
                    self.resources_for_plan[date][place] = resources[date][place]
                    self.components[date][place] = []

    def __getitem__(self, key):
        if key in self.places_with_all:
            return self.places_with_all[key]
        if key in self.dates_for_plan:
            return self.dates_for_plan[key]
        
    def clear_dates(self):
        for date in self.dates_for_plan:
            for place in self.dates_for_plan[date]:
                self.dates_for_plan[date][place] = []

    def clear_resources(self):
        pass
