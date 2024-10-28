from Core.Components.Compute.Constants import EPSILON
from Core.Components.Compute.Constants import update_interface
from Core.Components.Compute.BaseComputeYear import BaseComputeYear

import numpy as np
import copy as c
import itertools as it
import datetime as dt
from dateutil.relativedelta import relativedelta


class RegularCompute(BaseComputeYear):
    def __init__(self, parent):
        super().__init__(parent)

    @update_interface
    def __call__(self):
        self.variants = {}
        self.__collect_plan_variants(0, 0)
        self.k_variants = {}
        self.sr_variants = {}
        self.usefull_useless_variants = {}
        self.__calculate_k_for_plans()
        self.curr_k = 0
        self.choosen_variant = tuple(self.variants)[-1]
        self.__choose_variant()
        self.__update_plan()
        self.__update_remains()

    def __collect_plan_variants(self, num, summ, var=()):
        if num == len(self.place_names):
            self.variants[var] = summ
            return
        place = self.place_names[num]
        self.__collect_plan_variants(num+1, summ, var+(0,))
        if summ >= self.speed:
            return
        lim_layer = self.core['parameters']['max_dh'][place]
        for i, layer in enumerate(reversed(sorted(list(self.remains[place]))), 1):
            if i > lim_layer:
                break
            next_m = self.remains[place][layer]['SUMM']['M']
            if summ + next_m > self.speed:
                i = i + (self.speed - summ) / next_m - 1
                summ = self.speed
            else:
                summ += next_m
            self.__collect_plan_variants(num+1, summ, var+(i,))
            # ~~optimization
            if summ >= self.speed:
                break
            # ~~

    def __calculate_k_for_plans(self):
        for variant in self.variants:
            v_usefull = 0
            m_usefull = 0
            v_useless = 0
            m_useless = 0
            for i_place, num_of_layers in enumerate(variant):
                place = self.place_names[i_place]
                i_layer = 0
                while i_layer < num_of_layers:
                    horizont = sorted(list(self.remains[place]))[-1-i_layer]
                    for ore in self.core['parameters']['usefull_ores']:
                        usefull_flag = self.core['parameters']['usefull_ores'][ore]
                        if ore in self.remains[place][horizont]['ORE']:
                            ore_v = self.remains[place][horizont]['ORE'][ore]['V']
                            ore_m = self.remains[place][horizont]['ORE'][ore]['M']
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
                self.k_variants[variant] = float('-inf')
                self.sr_variants[variant] = float('-inf')
            else:
                self.k_variants[variant] = self.k_calculate(v_usefull, m_usefull, v_usefull+v_useless, m_usefull+m_useless)
                self.sr_variants[variant] = self.stripping_ratio_calculate(v_usefull, m_usefull, v_useless, m_useless)
            self.usefull_useless_variants[variant] = (v_usefull, m_usefull, v_useless, m_useless)

    def __choose_variant(self):
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

    def __update_plan(self):
        DELTAS = {
            1: relativedelta(years=1),
            2: relativedelta(months=6),
            4: relativedelta(months=3),
            12: relativedelta(months=1),
            53: relativedelta(weeks=1),
        }
        date_start = tuple(self.core['plan'])[-1]
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
            horizonts = list(reversed(sorted(list(self.remains[place]))))
            layers_by_time = [self.remains[place][horizonts[i]]['SUMM']['M'] for i in range(int(num_of_layers))]
            if num_of_layers % 1 > 0:
                layers_by_time.append(self.remains[place][horizonts[int(num_of_layers)]]['SUMM']['M'] * (num_of_layers % 1))
            summ_of_mass = sum(layers_by_time)
            for i_date in range(1, self.date_scale+1):
                new_date = str((dt.datetime.strptime(date_start, "%Y-%m-%d") + timedelta * i_date).date())
                summ = summ_of_mass / self.date_scale * i_date
                if new_date not in self.core['plan']:
                    self.core['plan'][new_date] = {}
                if place not in self.core['plan'][new_date]:
                    self.core['plan'][new_date][place] = []    
                # --------optimization--------
                if not summ:
                    continue
                # --------
                # ----------logging-----------
                self.log_variants[new_date, place] = num_of_layers
                self.log_ores[new_date, place] = {}
                self.log_components[new_date, place] = np.zeros(len(self.core['component_types']))
                self.log_places[new_date, place] = summ
                # ----------------------------
                i_layer = 0
                while iter_mass < summ-EPSILON:
                    horizont = sorted(list(self.remains[place]))[-1-i_layer]
                    if i_layer >= len(layers_by_time):
                        i_layer -= 1
                    if layers_by_time[i_layer] < EPSILON:
                        k = 0
                        i_layer += 1
                        continue
                    elif layers_by_time[i_layer] > (summ - iter_mass):
                        k = (summ - iter_mass) / self.remains[place][horizont]['SUMM']['M']
                        layers_by_time[i_layer] -= summ - iter_mass
                        iter_mass = summ
                    elif layers_by_time[i_layer] <= (summ - iter_mass):
                        k = layers_by_time[i_layer] / self.remains[place][horizont]['SUMM']['M']
                        iter_mass += layers_by_time[i_layer]
                        layers_by_time[i_layer] = 0
                    for ore in self.remains[place][horizont]['ORE']:
                        v = self.remains[place][horizont]['ORE'][ore]['V'] * k
                        m = self.remains[place][horizont]['ORE'][ore]['M'] * k
                        components = self.remains[place][horizont]['ORE'][ore]['COMPONENTS'] * self.components_changes
                        plan_record = [horizont, ore, v, m] + list(components)
                        self.core['plan'][new_date][place].append(tuple(plan_record))
                        # ----------logging-------------
                        if ore not in self.log_ores[new_date, place]:
                            self.log_ores[new_date, place][ore] = 0
                        self.log_ores[new_date, place][ore] = self.remains[place][horizont]['ORE'][ore]['M']
                        self.log_components[new_date, place] = components
                        # ------------------------------
                    i_layer += 1

    def __update_remains(self):
        if self.choosen_variant == ():
            return
        for i_place, num_of_layers in enumerate(self.choosen_variant):
            place = self.place_names[i_place]
            i_layer = 0
            while i_layer < num_of_layers:
                if not self.remains[place]:
                    break
                horizont = sorted(list(self.remains[place]))[-1]
                k = num_of_layers - i_layer
                if k >= 1:
                    self.remains[place].pop(horizont)
                    i_layer += 1
                    continue
                self.remains[place][horizont]['SUMM']['V'] -= self.remains[place][horizont]['SUMM']['V'] * k
                self.remains[place][horizont]['SUMM']['M'] -= self.remains[place][horizont]['SUMM']['M'] * k
                for ore in self.remains[place][horizont]['ORE']:
                    self.remains[place][horizont]['ORE'][ore]['V'] -= self.remains[place][horizont]['ORE'][ore]['V'] * k
                    self.remains[place][horizont]['ORE'][ore]['M'] -= self.remains[place][horizont]['ORE'][ore]['M'] * k
                i_layer += 1
