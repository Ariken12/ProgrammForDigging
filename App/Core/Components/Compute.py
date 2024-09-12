import Core.Core
import numpy as np
import copy as c
import itertools as it


EPSILON = 10 ** -6


class Compute:
    def __init__(self, core):
        self.core : Core.Core = core
        self.data : Core.Data = core.data
        self.remains = {}
        self.k_calculate = lambda v_u, m_u, v_a, m_a: 0
        self.date_scale = 1
        self.output = ['', '', '', '', '']
        self.speed = 0


    def main_calculate(self):
        proc = self.load_parameters() 
        while (output := next(proc)):
            yield output
        proc = self.load_remains()
        while (output := next(proc)):
            yield output
        proc = self.calculate_years()
        while (output := next(proc)):
            yield output
        yield None

    def calculate_years(self):
        acceleration = self.data.parameters['acceleration']
        self.speed = acceleration[0]
        print(self.speed)
        i_speed = 0
        end_i_speed = len(acceleration) - 1
        year = 1
        self.log(0, f'Год {year}')
        yield self.log(1, f'Скорость {self.speed}')
        while self.check_empty_carreer():
            self.calculate_carreer_digging()
            if i_speed != end_i_speed:
                i_speed += 1
                self.speed = acceleration[i_speed]
                self.log(1, f'Скорость {self.speed}')
            year += 1
            yield self.log(0, f'Год {year}')
            break
        yield None

    def calculate_carreer_digging(self):
        self.collection = tuple(self.data.places.keys())
        self.variants = {}
        self.collect_plan_variants(0, 0)
        print(self.variants)
        self.calculate_k_for_plans()

    def collect_plan_variants(self, num, summ, var=()):
        if num == len(self.collection):
            self.variants[var] = summ
            return
        place = self.collection[num]
        self.collect_plan_variants(num+1, summ, var+(0,))
        for i, layer in enumerate(self.remains[place], 1):
            next_m = self.remains[place][layer]['SUMM']['M']
            if next_m + summ > self.speed:
                i = i + (self.speed - summ) / next_m - 1
            summ = self.speed
            self.collect_plan_variants(num+1, summ, var+(i,))
            # ~~optimization
            if summ >= self.speed:
                break
            # ~~

    def calculate_k_for_plans(self):
        self.k_variants = {}
        for variant in self.variants:
            for i_place in variant:
                pass

    def update_remains(self):
        max = 0
        for variant in self.variants:
            if self.variants[variant] > max:
                max = self.variants
        

    def load_parameters(self):
        self.k_calculate = {
            'M / M': lambda v_u, m_u, v_a, m_a: m_u / m_a, 
            'V / M': lambda v_u, m_u, v_a, m_a: v_u / m_a, 
            'V / V': lambda v_u, m_u, v_a, m_a: v_u / v_a
        }[self.data.parameters['k_func']]
        self.date_scale = {
            'Год': 1, 
            'Полугодие': 2, 
            'Сезон': 4, 
            'Месяц': 12, 
            'Неделя': 52
        }[self.data.parameters['step_date']]
        yield None 
    
    def load_remains(self):
        for row in self.data.table:
            place = row[0]
            horizont = row[1]
            type_of_ore = row[2]
            v = row[3]
            m = row[4]
            sg = row[5]
            components = np.array(row[6:16])
            if place not in self.remains:
                self.remains[place] = {}
            if horizont not in self.remains[place]:
                self.remains[place][horizont] = {
                    'SUMM': 
                        {'V': 0, 'M': 0, 'COMPONENTS': np.zeros((10,))}, 
                    'ORES':
                        {}}
            if type_of_ore not in self.remains[place][horizont]['ORES']:
                self.remains[place][horizont]['ORES'][type_of_ore] = {'V': 0, 'M': 0, 'COMPONENTS': np.zeros((10,))}
            self.remains[place][horizont]['SUMM']['V'] += v
            self.remains[place][horizont]['SUMM']['M'] += m
            self.remains[place][horizont]['SUMM']['COMPONENTS'] += components
            self.remains[place][horizont]['ORES'][type_of_ore]['V'] += v
            self.remains[place][horizont]['ORES'][type_of_ore]['M'] += m
            self.remains[place][horizont]['ORES'][type_of_ore]['COMPONENTS'] += components
            yield f'Загружена {type_of_ore} на {horizont} горизонте, на участке {place}'
        yield 'Таблица руд загружена в вычислитель'
        yield None

    def check_empty_carreer(self):
        M = 0
        for place in self.remains:
            for horizont in self.remains[place]:
                M += self.remains[place][horizont]['SUMM']['M']
        return M > EPSILON

    
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

    def log(self, i, text):
        self.output[i] = text
        return '\n'.join(self.output)