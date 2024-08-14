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
                components = [0] * 10
                mass = 0
                self.data.components[key_date][key_place] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                place = list(resources[key_date][key_place])
                rows = list(reversed(sorted(filter(lambda x: x[0] == key_place, self.data.table), key=lambda x: x[1])))
                result = []
                horizont = -1
                for row in rows:
                    if horizont != row[1]:
                        result = [row[1], row[2], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    index = self.data.ore_types.index(row[2])
                    value = row[3]        # Обьем
                    if place[index] <= 0:
                        continue
                    if place[index] < value:
                        result[2] = place[index]       # Обьем
                        k = result[2] / value          # Обьем
                        place[index] = 0
                    else:
                        result[2] = value     # Обьем
                        k = 1
                        place[index] -= value
                    result[3] = row[4] * k   # Масса
                    for i in range(10):
                        result[4+i] = row[i+6] * (k)
                    self.data.plan[key_date][key_place].append(tuple(result))
                    for i, component in enumerate(result[4:]):
                        components[i] += component * row[4] 
                    mass += row[4] * k
                for i, component in enumerate(components):
                    self.data.components[key_date][key_place][i] = component / mass if mass != 0 else 0

