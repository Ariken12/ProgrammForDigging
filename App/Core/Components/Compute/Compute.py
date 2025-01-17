from Core.Components.Compute.RegularCompute import RegularCompute
from Core.Components.Compute.CustomCompute import CustomCompute
from Core.Components.Compute.Constants import EPSILON


import Core.Core
import numpy as np
import matplotlib.pyplot as plt
import openpyxl as opx


class Compute:
    def __init__(self, core):
        self.core : Core.Core = core
        self.place_names = None
        self.k_calculate = None
        self.stripping_ratio_calculate = None
        self.date_scale = None
        self.components_changes = None
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
        self.__regular_compute = RegularCompute(self)
        self.__custom_compute = CustomCompute(self)

    @staticmethod
    def k_calculate(v_u, m_u, v_a, m_a):
        return 0

    def __call__(self):
        proc = self.__load_parameters() 
        while (output := next(proc)):
            yield output
        proc = self.__load_remains()
        while (output := next(proc)):
            yield output
        proc = self.__calculate_years()
        while (output := next(proc)):
            yield output
        yield None

    def __calculate_years(self):
        yield self.__log(4, 'Рассчет плана')
        acceleration = self.core['parameters']['acceleration']
        self.speed = acceleration[0]
        i_speed = 0
        end_i_speed = len(acceleration) - 1
        self.year = 0
        self.core['plan'] = {}
        self.core['plan'][self.core['parameters']['begin_date']] = {}
        for place in self.core['remains']:
            self.core['plan'][self.core['parameters']['begin_date']][place] = []
        self.__log(0, f'Год {self.year}')
        self.ok = True
        yield self.__log(1, f'Скорость {self.speed}')
        while (summ_of_remain := self.__check_empty_carreer()) > EPSILON:
            print(summ_of_remain)
            self.year += 1
            try:
                if self.core['plan_modify']:
                    self.__custom_compute()
                self.__regular_compute()
            except Exception as e:
                self.ok = False
                self.__log(3, f'Ошибка в вычислениях: {type(e)}: {e}')
                raise e
            if i_speed != end_i_speed:
                i_speed += 1
                self.speed = acceleration[i_speed]
                self.__log(1, f'Скорость {self.speed}')
            yield self.__log(0, f'Год {self.year}')
        yield self.__log(0, f'План включает {self.year} лет/года')
        yield self.__log(1, '')
        yield self.__log(2, '')
        if self.ok:
            yield self.__log(3, '')
        yield self.__log(4, 'Запись отчета')
        self.__write_output()
        yield self.__log(4, 'Рассчет закончен, Отчет записан')
        yield None

    @staticmethod
    def __m2m(v_u, m_u, v_a, m_a): return m_u / m_a
    
    @staticmethod
    def __v2m(v_u, m_u, v_a, m_a): return v_u / m_a
    
    @staticmethod
    def __v2v(v_u, m_u, v_a, m_a): return v_u / v_a

    @staticmethod
    def __mm(v_uf, m_uf, v_ul, m_ul): return (m_ul / m_uf) if m_uf != 0 else 0
    
    @staticmethod
    def __vm(v_uf, m_uf, v_ul, m_ul): return (v_ul / m_uf) if m_uf != 0 else 0
    
    @staticmethod
    def __vv(v_uf, m_uf, v_ul, m_ul): return (v_ul / v_uf) if v_uf != 0 else 0
    
    def __load_parameters(self):
        self.place_names = self.core['places']
        self.k_calculate = {
            'M / M': self.__m2m, 
            'V / M': self.__v2m, 
            'V / V': self.__v2v
        }[self.core['parameters']['k_func']]
        self.stripping_ratio_calculate = {
            'M / M': self.__mm, 
            'V / M': self.__vm, 
            'V / V': self.__vv
        }[self.core['parameters']['k_func']]
        self.date_scale = {
            'Год': 1, 
            'Полугодие': 2, 
            'Квартал': 4, 
            'Месяц': 12, 
            'Неделя': 53
        }[self.core['parameters']['step_date']]
        self.components_changes = [1] * len(self.core['component_types'])
        for i, val in enumerate(self.core['parameters']['measure_count']):
            if ('г/т' in self.core['component_types'][i].lower() and self.core['parameters']['measure_count'][val] == 0):
                self.components_changes[i] = 10
                self.core['component_types'] = tuple([component.replace('г/т', '%') if j == i else component for j, component in enumerate(self.core['component_types'])])
            if ('%' in self.core['component_types'][i].lower() and self.core['parameters']['measure_count'][val] == 1):
                self.components_changes[i] = 0.1
                self.core['component_types'] = tuple([component.replace('%', 'г/т') if j == i else component for j, component in enumerate(self.core['component_types'])])
        self.components_changes = np.array(self.components_changes)
        self.log_variants.clear()
        self.log_k.clear()
        self.log_speed.clear()
        self.log_ores.clear()
        self.log_components.clear()
        self.log_places.clear()
        self.log_stripping_ratio.clear()
        yield None 
    
    def __load_remains(self):
        yield self.__log(4, 'Подготовка данных для обработки')
        for row in self.core['table']:
            place = row[0]
            horizont = row[1]
            type_of_ore = row[2]
            v = row[3]
            m = row[4]
            components = np.array(row[6:16])
            if place not in self.core['remains']:
                self.core['remains'][place] = {}
            if horizont not in self.core['remains'][place]:
                self.core['remains'][place][horizont] = {
                    'SUMM': 
                        {'V': 0, 'M': 0, 'COMPONENTS': np.zeros((len(self.core['component_types']),))}, 
                    'ORE':
                        {}}
            if type_of_ore not in self.core['remains'][place][horizont]['ORE']:
                self.core['remains'][place][horizont]['ORE'][type_of_ore] = {'V': 0, 'M': 0, 'COMPONENTS': np.zeros((len(self.core['component_types']),))}
            self.core['remains'][place][horizont]['SUMM']['V'] += v
            self.core['remains'][place][horizont]['SUMM']['M'] += m
            self.core['remains'][place][horizont]['SUMM']['COMPONENTS'] += components
            self.core['remains'][place][horizont]['ORE'][type_of_ore]['V'] += v
            self.core['remains'][place][horizont]['ORE'][type_of_ore]['M'] += m
            self.core['remains'][place][horizont]['ORE'][type_of_ore]['COMPONENTS'] += components
            yield self.__log(0, f'Загружена {type_of_ore} на {horizont} горизонте, на участке {place}')
        yield self.__log(4, 'Таблица руд загружена в вычислитель')
        yield None

    def __write_output(self):
        try:
            plt.plot(range(1, len(self.log_k)+1), list(self.log_k), label='Коэффициент добычи')
            plt.xlabel('Количество лет в отработке')
            plt.ylabel(f'Коэффициент добычи, {self.core['parameters']['k_func'][::-1]}')
            plt.savefig('Коэффициент добычи.png', dpi=300)
            plt.clf()
            plt.plot(range(1, len(self.log_stripping_ratio)+1), list(self.log_stripping_ratio), label='Коэффициент вскрыши')
            plt.xlabel('Количество лет в отработке')
            plt.ylabel(f'Коэффициент вскрыши, {self.core['parameters']['k_func']}')
            plt.savefig('Коэффициент вскрыши.png', dpi=300)
            plt.clf()
            plt.plot(range(1, len(self.log_speed)+1), self.log_speed, label='Общая скорость добычи')
            plt.xlabel('Количество лет в отработке')
            plt.ylabel(f'Общая скорость добычи, т')
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
            self.__log(1, 'Не удалось сохранить графики')
        wb = opx.Workbook()
        wb.remove(wb.active)
        wb.create_sheet('План')
        ws = wb.active

        output = ['Год', 'Сумма за год', 'Коэффициент вскрыши', 'Участок', 'Сумма на участке', 'Горизонт', \
                  'Наименование руды', 'Обьем руды', 'Масса руды'] + list(self.core['component_types'])
        for col in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            ws.column_dimensions[col].width = 15
        ws.append(output)

        plan = self.core['plan']
        years = [year for year in tuple(plan)[1:]]
        for iyear, year in enumerate(years):
            places = tuple(plan[year])
            for iplace, place in enumerate(places):
                for idata, data in enumerate(plan[year][place]):
                    if (year, place) not in self.log_places:
                        continue
                    summ = self.log_speed[iyear // self.date_scale]
                    k_useless = self.log_stripping_ratio[iyear // self.date_scale]
                    summ_of_place = self.log_places[year, place]
                    horizont = data[0]
                    ore_name = data[1]
                    v_of_ore = data[2]
                    m_of_ore = data[3]
                    components = list(data[4:])
                    output = [year, summ, k_useless, place, summ_of_place, horizont, ore_name, v_of_ore, m_of_ore] + components
                    ws.append(output)
        try:
            wb.save('План горных работ.xlsx')
        except Exception as e:
            self.__log(2, 'Ошибка записи Excel файла')


    def __check_empty_carreer(self):
        M = 0
        for place in self.core['remains']:
            for horizont in self.core['remains'][place]:
                M += self.core['remains'][place][horizont]['SUMM']['M']
        return M

    def __log(self, i, text):
        self.output[i] = text
        return '\n'.join(self.output)
