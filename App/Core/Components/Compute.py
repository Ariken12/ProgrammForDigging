import Core.Core
import numpy as np
import copy as c
import itertools as it
import datetime as dt
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import openpyxl as opx



EPSILON = 10 ** -6
ABSOLUT_MAX = 10 ** 6


class Compute:
    def __init__(self, core):
        self.core : Core.Core = core
        self.data : Core.Data = core.data
        self.remains = {}
        self.k_calculate = lambda v_u, m_u, v_a, m_a: 0
        self.date_scale = 1
        self.output = ['', '', '', '', '']
        self.log_variants = {}
        self.log_k = []
        self.log_speed = []
        self.log_ores = {}
        self.log_components = {}
        self.log_places = {}
        self.log_stripping_ratio = []
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
        yield self.log(4, 'Рассчет плана')
        acceleration = self.data.parameters['acceleration']
        self.speed = acceleration[0]
        i_speed = 0
        end_i_speed = len(acceleration) - 1
        self.year = 0
        self.data.plan = {}
        self.data.plan[self.data.parameters['begin_date']] = {}
        for place in self.remains:
            self.data.plan[self.data.parameters['begin_date']][place] = []
        self.log(0, f'Год {self.year}')
        self.ok = True
        yield self.log(1, f'Скорость {self.speed}')
        while (summ_of_remain := self.check_empty_carreer()) > EPSILON:
            print(summ_of_remain)
            self.year += 1
            try:
                self.calculate_carreer_digging()
            except Exception as e:
                self.ok = False
                self.log(3, f'Ошибка в вычислениях: {type(e)}: {e}')
                raise e
            print(self.choosen_variant)
            if i_speed != end_i_speed:
                i_speed += 1
                self.speed = acceleration[i_speed]
                self.log(1, f'Скорость {self.speed}')
            yield self.log(0, f'Год {self.year}')
        yield self.log(0, f'План включает {self.year} лет/года')
        yield self.log(1, '')
        yield self.log(2, '')
        if self.ok:
            yield self.log(3, '')
        yield self.log(4, 'Запись отчета')
        self.write_output()
        yield self.log(4, 'Рассчет закончен, Отчет записан')
        yield None

    def calculate_carreer_digging(self):
        self.place_names = tuple(self.data.places.keys())
        self.variants = {}
        self.collect_plan_variants(0, 0)
        self.k_variants = {}
        self.sr_variants = {}
        self.calculate_k_for_plans()
        self.curr_k = 0
        self.choosen_variant =tuple(self.variants)[-1]
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
                i = i + (self.speed - summ) / next_m - 1
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
            self.sr_variants[variant] = self.stripping_ratio_calculate(v_usefull, m_usefull, v_useless, m_useless)

    def choose_variant(self):
        max_speed = 0
        for variant in self.variants:
            if self.variants[variant] > max_speed:
                max_speed = self.variants[variant]
        for variant in self.variants:
            if not max_speed - EPSILON < self.variants[variant] < max_speed + EPSILON:
                continue
            if self.k_variants[variant] > self.curr_k:
                self.curr_k = self.k_variants[variant]
                self.choosen_variant = variant
                self.log(2, f'Оптимальный вариант для этого года - {self.choosen_variant}')
                self.log(3, f'Оптимальный коэффициент полезной руды - {self.curr_k}')

    def update_plan(self):
        DELTAS = {
            1: relativedelta(years=1),
            2: relativedelta(months=6),
            4: relativedelta(months=3),
            12: relativedelta(months=1),
            53: relativedelta(weeks=1),
        }
        date_start = tuple(self.data.plan)[-1]
        timedelta = DELTAS[self.date_scale]
        # ------------logging-------------------
        variant = self.choosen_variant
        self.log_speed.append(self.variants[variant])
        self.log_k.append(self.k_variants[variant])
        self.log_stripping_ratio.append(self.sr_variants[variant])
        # -------------------------------
        for i_place, num_of_layers in enumerate(self.choosen_variant):
            place = self.place_names[i_place]
            summ = 0
            iter_mass = 0
            horizonts = tuple(self.remains[place])
            layers_by_time = [self.remains[place][horizonts[i]]['SUMM']['M'] for i in range(int(num_of_layers))]
            if num_of_layers % 1 > 0:
                layers_by_time.append(self.remains[place][horizonts[int(num_of_layers)]]['SUMM']['M'] * (num_of_layers % 1))
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
                # ----------logging-----------
                self.log_variants[new_date, place] = num_of_layers
                self.log_ores[new_date, place] = {}
                self.log_components[new_date, place] = np.zeros(len(self.data.components_types))
                self.log_places[new_date, place] = summ
                # ----------------------------
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
                        k = (summ - iter_mass) / self.remains[place][horizont]['SUMM']['M']
                        iter_mass = summ
                        layers_by_time[i_layer] -= summ - iter_mass
                    elif layers_by_time[i_layer] <= (summ - iter_mass):
                        k = layers_by_time[i_layer] / self.remains[place][horizont]['SUMM']['M']
                        iter_mass += layers_by_time[i_layer]
                        layers_by_time[i_layer] = 0
                    for ore in self.remains[place][horizont]['ORE']:
                        v = self.remains[place][horizont]['ORE'][ore]['V'] * k
                        m = self.remains[place][horizont]['ORE'][ore]['M'] * k
                        components = self.remains[place][horizont]['ORE'][ore]['COMPONENTS']
                        plan_record = [horizont, ore, v, m] + list(components)
                        self.data.plan[new_date][place].append(tuple(plan_record))
                        # ----------logging-------------
                        if ore not in self.log_ores[new_date, place]:
                            self.log_ores[new_date, place][ore] = 0
                        self.log_ores[new_date, place][ore] = self.remains[place][horizont]['ORE'][ore]['M']
                        self.log_components[new_date, place] = components
                        # ------------------------------
                    i_layer += 1


    def update_remains(self):
        if self.choosen_variant == ():
            return
        for i_place, num_of_layers in enumerate(self.choosen_variant):
            place = self.place_names[i_place]
            i_layer = 0
            while i_layer < num_of_layers:
                if not self.remains[place]:
                    break
                horizont = tuple(self.remains[place])[0]
                k = num_of_layers - i_layer
                if k > 1:
                    self.remains[place].pop(horizont)
                    i_layer += 1
                    continue
                self.remains[place][horizont]['SUMM']['V'] -= self.remains[place][horizont]['SUMM']['V'] * k
                self.remains[place][horizont]['SUMM']['M'] -= self.remains[place][horizont]['SUMM']['M'] * k
                self.remains[place][horizont]['SUMM']['COMPONENTS'] = self.remains[place][horizont]['SUMM']['COMPONENTS']
                for ore in self.remains[place][horizont]['ORE']:
                    self.remains[place][horizont]['ORE'][ore]['V'] -= self.remains[place][horizont]['ORE'][ore]['V'] * k
                    self.remains[place][horizont]['ORE'][ore]['M'] -= self.remains[place][horizont]['ORE'][ore]['M'] * k
                    self.remains[place][horizont]['ORE'][ore]['COMPONENTS'] = self.remains[place][horizont]['ORE'][ore]['COMPONENTS']
                i_layer += 1

    def write_output(self):
        try:
            plt.plot(range(1, len(self.log_k)+1), list(self.log_k))
            plt.savefig('Коэффициент добычи.png', dpi=300)
            plt.clf()
            plt.plot(range(1, len(self.log_k)+1), list(self.log_stripping_ratio))
            plt.savefig('Коэффициент вскрыши.png', dpi=300)
            plt.clf()
            plt.plot(range(1, len(self.log_speed)+1), self.log_speed)
            plt.savefig('Общая скорость добычи.png', dpi=300)
            plt.clf()
            # places = {}
            # for year, place in self.log_places:
            #     if place not in places:
            #         places[place] = {'x': [], 'y': []}
            #     places[place]['x'].append(self.log_places[year, place])
            #     places[place]['y'].append(len(places[place]['x']))
            # for place in places:
            #     plt.plot(places[place]['y'], places[place]['x'], label=place)
            # plt.savefig(f'Скорость добычи по участкам.png', dpi=300)
            # plt.clf()
            # for place in places:
            #     plt.plot(places[place]['y'], places[place]['x'], label=place)
            #     plt.savefig(f'Скорость добычи {place}.png', dpi=300)
            #     plt.clf()
        except Exception as e:
            self.log(1, 'Не удалось сохранить графики')
        self.wb = opx.Workbook()
        self.ws = self.wb.active

        output = ['Год', 'Сумма за год', 'Коэффициент вскрыши', 'Участок', 'Сумма на участке', 'Горизонт', \
                  'Наименование руды', 'Обьем руды', 'Масса руды'] + list(self.data.components_types)
        for col in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            self.ws.column_dimensions[col].width = 15
        self.ws.append(output)

        plan = self.data.plan
        years = [year for year in tuple(plan)[1:]]
        for iyear, year in enumerate(years):
            places = tuple(plan[year])
            for iplace, place in enumerate(places):
                for idata, data in enumerate(plan[year][place]):
                    if (year, place) not in self.log_places:
                        continue
                    summ = self.log_speed[iyear // self.date_scale]
                    k_useless = self.log_k[iyear // self.date_scale]
                    summ_of_place = self.log_places[year, place]
                    horizont = data[0]
                    ore_name = data[1]
                    v_of_ore = data[2]
                    m_of_ore = data[3]
                    components = list(data[4:])
                    output = [year, summ, k_useless, place, summ_of_place, horizont, ore_name, v_of_ore, m_of_ore] + components
                    self.ws.append(output)
        try:
            self.wb.save('План горных работ.xlsx')
        except Exception as e:
            self.log(2, 'Ошибка записи Excel файла')

    def load_parameters(self):
        self.k_calculate = {
            'M / M': lambda v_u, m_u, v_a, m_a: m_u / m_a, 
            'V / M': lambda v_u, m_u, v_a, m_a: v_u / m_a, 
            'V / V': lambda v_u, m_u, v_a, m_a: v_u / v_a
        }[self.data.parameters['k_func']]
        self.stripping_ratio_calculate = {
            'M / M': lambda v_uf, m_uf, v_ul, m_ul: (m_ul / m_uf) if m_uf != 0 else 0, 
            'V / M': lambda v_uf, m_uf, v_ul, m_ul: (v_ul / m_uf) if m_uf != 0 else 0, 
            'V / V': lambda v_uf, m_uf, v_ul, m_ul: (v_ul / v_uf) if v_uf != 0 else 0
        }[self.data.parameters['k_func']]
        self.date_scale = {
            'Год': 1, 
            'Полугодие': 2, 
            'Квартал': 4, 
            'Месяц': 12, 
            'Неделя': 53
        }[self.data.parameters['step_date']]
        self.log_variants.clear()
        self.log_k.clear()
        self.log_speed.clear()
        self.log_ores.clear()
        self.log_components.clear()
        self.log_places.clear()
        self.log_stripping_ratio.clear()
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
                        {'V': 0, 'M': 0, 'COMPONENTS': np.zeros((len(self.data.components_types),))}, 
                    'ORE':
                        {}}
            if type_of_ore not in self.remains[place][horizont]['ORE']:
                self.remains[place][horizont]['ORE'][type_of_ore] = {'V': 0, 'M': 0, 'COMPONENTS': np.zeros((len(self.data.components_types),))}
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