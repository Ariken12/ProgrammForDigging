import Core.Core
import numpy as np
import copy as c
import itertools as it
import datetime as dt
import matplotlib.pyplot as plt
import openpyxl as opx



EPSILON = 10 ** -3


class Compute:
    def __init__(self, core):
        self.core : Core.Core = core
        self.data : Core.Data = core.data
        self.remains = {}
        self.k_calculate = lambda v_u, m_u, v_a, m_a: 0
        self.date_scale = 1
        self.output = ['', '', '', '', '']
        self.log_variants = []
        self.log_k = []
        self.log_speed = []
        self.log_ores = []
        self.log_components = []
        self.log_all = []
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
        yield self.log(4, 'Рассчеты завершены')
        yield None

    def calculate_years(self):
        yield self.log(4, 'Рассчет плана')
        acceleration = self.data.parameters['acceleration']
        self.wb = opx.Workbook()
        self.ws = self.wb.active
        self.speed = acceleration[0]
        i_speed = 0
        end_i_speed = len(acceleration) - 1
        self.year = 0
        self.data.plan = {}
        self.data.plan[self.data.parameters['begin_date']] = {}
        for place in self.remains:
            self.data.plan[self.data.parameters['begin_date']][place] = []
        self.log(0, f'Год {self.year}')
        yield self.log(1, f'Скорость {self.speed}')
        while self.check_empty_carreer() > EPSILON:
            self.year += 1
            self.calculate_carreer_digging()
            print(self.choosen_variant)
            if i_speed != end_i_speed:
                i_speed += 1
                self.speed = acceleration[i_speed]
                self.log(1, f'Скорость {self.speed}')
            self.logging()
            yield self.log(0, f'Год {self.year}')
        self.write_output()
        yield None

    def calculate_carreer_digging(self):
        self.place_names = tuple(self.data.places.keys())
        self.variants = {}
        self.collect_plan_variants(0, 0)
        self.k_variants = {}
        self.calculate_k_for_plans()
        self.curr_k = 0
        self.choosen_variant = ()
        self.choose_variant()
        self.update_plan()
        self.update_remains()
        

    def collect_plan_variants(self, num, summ, var=()):
        if num == len(self.place_names):
            self.variants[var] = summ
            self.log(2, f'Обработан вариант {var}')
            return
        place = self.place_names[num]
        self.collect_plan_variants(num+1, summ, var+(0,))
        if summ >= self.speed:
            return
        lim_layer = self.data.parameters['max_dh'][place]
        for i, layer in enumerate(self.remains[place], 1):
            if i > lim_layer:
                break
            next_m = self.remains[place][layer]['SUMM']['M']
            summ_of_layer = self.all_resources[place][layer]['SUMM']['M']
            if summ + next_m > self.speed:
                i = i + (self.speed - summ) / summ_of_layer - 1
                summ = self.speed
            else:
                summ += next_m
            self.collect_plan_variants(num+1, summ, var+(i,))
            # ~~optimization
            if summ >= self.speed:
                break
            # ~~

    def calculate_k_for_plans(self):
        for variant in self.variants:
            v_usefull = 0
            m_usefull = 0
            v_useless = 0
            m_useless = 0
            for i_place, num_of_layers in enumerate(variant):
                place = self.place_names[i_place]
                i_layer = 0
                while i_layer < num_of_layers:
                    horizont = tuple(self.remains[place])[i_layer]
                    for ore in self.data.parameters['usefull_ores']:
                        usefull_flag = self.data.parameters['usefull_ores'][ore]
                        if ore in self.all_resources[place][horizont]['ORE']:
                            ore_v = self.all_resources[place][horizont]['ORE'][ore]['V']
                            ore_m = self.all_resources[place][horizont]['ORE'][ore]['M']
                        else:
                            ore_v = 0
                            ore_m = 0
                        k = num_of_layers - i_layer
                        if k < 1:
                            ore_v *= k
                            ore_m *= k
                        if usefull_flag:
                            v_usefull += ore_v
                            m_usefull += ore_m
                        else:
                            v_useless += ore_v
                            m_useless += ore_m
                    i_layer += 1
            if (v_usefull == v_useless == m_usefull == m_useless == 0):
                continue
            self.k_variants[variant] = self.k_calculate(v_usefull, m_usefull, v_usefull+v_useless, m_usefull+m_useless)

    def choose_variant(self):
        max_speed = 0
        for variant in self.variants:
            if self.variants[variant] > max_speed:
                max_speed = self.variants[variant]
        for variant in self.variants:
            if self.variants[variant] != max_speed:
                continue
            if self.k_variants[variant] > self.curr_k:
                self.curr_k = self.k_variants[variant]
                self.choosen_variant = variant
                self.log(2, f'Оптимальный вариант для этого года - {self.choosen_variant}')
                self.log(3, f'Оптимальный коэффициент полезной руды - {self.curr_k}')

    def update_plan(self):
        date_start = tuple(self.data.plan)[-1]
        timedelta = dt.timedelta(milliseconds=24 * 60 * 60 * 365 * 1000 / self.date_scale)
        for i_place, num_of_layers in enumerate(self.choosen_variant):
            place = self.place_names[i_place]
            summ = 0
            iter_mass = 0
            # todo: написать распределение плана в течении года
            horizonts = tuple(self.remains[place])
            layers_by_time = [self.remains[place][horizonts[i]]['SUMM']['M'] for i in range(int(num_of_layers))]
            if num_of_layers % 1 > 0:
                layers_by_time.append(self.remains[place][horizonts[int(num_of_layers)]]['SUMM']['M'] * (num_of_layers % 1))
            layers_by_all = layers_by_time.copy()
            summ_of_mass = sum(layers_by_time)
            for i_date in range(1, self.date_scale+1):
                new_date = str((dt.datetime.strptime(date_start, "%Y-%m-%d") + timedelta * i_date).date())
                summ = summ_of_mass / self.date_scale * i_date
                if new_date not in self.data.plan:
                    self.data.plan[new_date] = {}
                if place not in self.data.plan[new_date]:
                    self.data.plan[new_date][place] = []    
                # --------optimization--------
                if not summ:
                    continue
                # --------
                # --------logging--------
                self.log_components.append(np.zeros(10))
                # --------
                i_layer = 0
                while iter_mass < summ-EPSILON:
                    horizont = tuple(self.remains[place])[i_layer]
                    if i_layer >= len(layers_by_time):
                        i_layer -= 1
                    if layers_by_time[i_layer] < EPSILON:
                        k = 0
                        i_layer += 1
                        continue
                    elif layers_by_time[i_layer] > (summ - iter_mass):
                        k = (summ - iter_mass) / layers_by_all[i_layer]
                        iter_mass += layers_by_all[i_layer] * k
                        layers_by_time[i_layer] -= layers_by_all[i_layer] * k
                    elif layers_by_time[i_layer] <= (summ - iter_mass):
                        k = layers_by_time[i_layer] / layers_by_all[i_layer]
                        iter_mass += layers_by_time[i_layer]
                        layers_by_time[i_layer] = 0
                    for ore in self.remains[place][horizont]['ORE']:
                        v = self.remains[place][horizont]['ORE'][ore]['V'] * k
                        m = self.remains[place][horizont]['ORE'][ore]['M'] * k
                        components = self.remains[place][horizont]['ORE'][ore]['COMPONENTS'] * k
                        # -------------logging-------------
                        self.log_components[-1] += components
                        # -------------logging-------------
                        plan_record = [horizont, ore, v, m] + list(components)
                        self.data.plan[new_date][place].append(tuple(plan_record))
                    
                    i_layer += 1

    def update_remains(self):
        if self.choosen_variant == ():
            return
        self.log_ores.append({})
        for i_place, num_of_layers in enumerate(self.choosen_variant):
            place = self.place_names[i_place]
            i_layer = 0
            while i_layer < num_of_layers:
                if not self.remains[place]:
                    break
                horizont = tuple(self.remains[place])[0]
                if num_of_layers - i_layer < 1:
                    k = num_of_layers - i_layer
                    self.remains[place][horizont]['SUMM']['V'] -= self.remains[place][horizont]['SUMM']['V'] * k
                    self.remains[place][horizont]['SUMM']['M'] -= self.remains[place][horizont]['SUMM']['M'] * k
                    self.remains[place][horizont]['SUMM']['COMPONENTS'] -= self.remains[place][horizont]['SUMM']['COMPONENTS'] * k
                    for ore in self.remains[place][horizont]['ORE']:
                        # -------------logging------------
                        if ore not in self.log_ores[-1]:
                            self.log_ores[-1][ore] = 0
                        self.log_ores[-1][ore] += self.remains[place][horizont]['ORE'][ore]['M'] * k
                        # -------------logging------------
                        self.remains[place][horizont]['ORE'][ore]['V'] -= self.remains[place][horizont]['ORE'][ore]['V'] * k
                        self.remains[place][horizont]['ORE'][ore]['M'] -= self.remains[place][horizont]['ORE'][ore]['M'] * k
                        self.remains[place][horizont]['ORE'][ore]['COMPONENTS'] -= self.remains[place][horizont]['ORE'][ore]['COMPONENTS'] * k
                        if self.remains[place][horizont]['ORE'][ore]['V'] < EPSILON or self.remains[place][horizont]['SUMM']['M'] < EPSILON:
                            self.remains[place].pop(horizont)
                            break
                    if horizont not in self.remains[place]:
                        continue
                    if self.remains[place][horizont]['SUMM']['V'] < EPSILON or self.remains[place][horizont]['SUMM']['M'] < EPSILON:
                        self.remains[place].pop(horizont)
                else:
                    self.remains[place].pop(horizont)
                i_layer += 1

    def logging(self):
        variant = self.choosen_variant
        self.log_variants.append(self.choosen_variant)
        self.log_k.append(self.k_variants[variant])
        self.log_speed.append(self.variants[variant])

    def write_output(self):
        plt.plot(range(1, len(self.log_k)+1), self.log_k)
        plt.savefig('Коэффициент полезной руды.png', dpi=300)
        plt.clf()
        plt.plot(range(1, len(self.log_speed)+1), self.log_speed)
        plt.savefig('Общая скорость добычи.png', dpi=300)
        plt.clf()
        ores = {}
        for i in range(1, len(self.log_ores)+1):
            for ore in self.log_ores[i-1]:
                if ore not in ores:
                    ores[ore] = {'x': [], 'y': []}
                if ore not in self.log_ores[i-1]:
                    continue
                ores[ore]['x'].append(i)
                ores[ore]['y'].append(self.log_ores[i-1][ore])
        for ore in ores:
            plt.plot(ores[ore]['x'], ores[ore]['y'], label=ore)
        plt.savefig(f'Скорость добычи руд.png', dpi=300)
        plt.clf()
        for ore in ores:
            plt.plot(ores[ore]['x'], ores[ore]['y'], label=ore)
            plt.savefig(f'Скорость добычи {ore}.png', dpi=300)
            plt.clf()
        plan = self.data.plan
        years = [year for year in tuple(plan)[1::self.date_scale]]
        for i, year in enumerate(years):
            for i_place, k in enumerate(self.choosen_variant):
                if k < 0:
                    continue
                place = self.place_names[i_place]
                ores = {}
                for ore in self.data.plan[year][place]:
                    pass

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
        self.log_variants.clear()
        self.log_k.clear()
        self.log_speed.clear()
        self.log_ores.clear()
        self.log_components.clear()
        self.log_all.clear()
        yield None 
    
    def load_remains(self):
        yield self.log(4, 'Загрузка руд в вычислитель')
        for row in self.data.table:
            place = row[0]
            horizont = row[1]
            type_of_ore = row[2]
            v = row[3]
            m = row[4]
            components = np.array(row[6:16])
            if place not in self.remains:
                self.remains[place] = {}
            if horizont not in self.remains[place]:
                self.remains[place][horizont] = {
                    'SUMM': 
                        {'V': 0, 'M': 0, 'COMPONENTS': np.zeros((10,))}, 
                    'ORE':
                        {}}
            if type_of_ore not in self.remains[place][horizont]['ORE']:
                self.remains[place][horizont]['ORE'][type_of_ore] = {'V': 0, 'M': 0, 'COMPONENTS': np.zeros((10,))}
            self.remains[place][horizont]['SUMM']['V'] += v
            self.remains[place][horizont]['SUMM']['M'] += m
            self.remains[place][horizont]['SUMM']['COMPONENTS'] += components
            self.remains[place][horizont]['ORE'][type_of_ore]['V'] += v
            self.remains[place][horizont]['ORE'][type_of_ore]['M'] += m
            self.remains[place][horizont]['ORE'][type_of_ore]['COMPONENTS'] += components
            yield self.log(0, f'Загружена {type_of_ore} на {horizont} горизонте, на участке {place}')
        self.all_resources = c.deepcopy(self.remains)
        yield self.log(4, 'Таблица руд загружена в вычислитель')
        yield None

    def check_empty_carreer(self):
        M = 0
        for place in self.remains:
            for horizont in self.remains[place]:
                M += self.remains[place][horizont]['SUMM']['M']
        return M

    
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