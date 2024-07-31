import Core.Core
import numpy as np

class Compute:
    def __init__(self, core):
        self.core : Core.Core = core
        self.data : Core.Data = core.data

    def calculate_places(self):
        resources = self.data.resources_for_plan
        self.data.clear_dates()
        for key_date in resources:
            for key_place in resources[key_date]:
                self.data.components[key_date][key_place] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                place = list(resources[key_date][key_place])
                rows = list(reversed(sorted(filter(lambda x: x[0] == key_place, self.data.table), key=lambda x: x[1])))
                result = []
                horizont = -1
                for row in rows:
                    if horizont != row[1]:
                        result = [row[1], row[2], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    index = self.data.ore_types.index(row[2])
                    value = row[3]
                    if place[index] <= 0:
                        continue
                    if place[index] < value:
                        result[2] = place[index]
                        k = result[2] / value
                        place[index] = 0
                    else:
                        result[2] = value
                        k = 1
                        place[index] -= value
                    for i in range(len(result)-3):
                        result[3+i] = row[i+6] * (k)
                    self.data.dates_for_plan[key_date][key_place].append(tuple(result))
                    for i, component in enumerate(result[3:]):
                        self.data.components[key_date][key_place][i] += component

