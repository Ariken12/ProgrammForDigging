
from typing import Any


EPSILON = 10 ** -6

__SHARED_VARS = ('remains',
    'place_names',
    'k_calculate',
    'stripping_ratio_calculate',
    'date_scale',
    'components_changes',
    'date_scale',
    'output',
    'log_variants',
    'log_k',
    'log_speed',
    'log_ores',
    'log_components',
    'log_places',
    'log_stripping_ratio',
    'speed')

def update_interface(method):
    def wrapper(self, *args, **kwargs):
        for var in __SHARED_VARS:
            self.__dict__[var] = self.parent.__dict__[var]
        val = method(self, *args, **kwargs)
        for var in __SHARED_VARS:
            self.parent.__dict__[var] = self.__dict__[var]
        return val
    return wrapper