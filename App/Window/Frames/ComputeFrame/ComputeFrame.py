import tkinter as tk
import tkinter.filedialog as fd
from tkinter import ttk
import sys
from datetime import datetime as dt
import numpy as np


from Window.Frames.ComputeFrame.Constants import *
from Window.Frames.CustomWidgets.ParametersFrame import ParametersFrame
from Window.Frames.CustomWidgets.AmountFrame import AmountFrame
from Window.Frames.CustomWidgets.InputParametersFrame import InputParametersFrame
from Window.Frames.CustomWidgets.FlawingOrderFrame import FlawingOrderFrame


class ComputeFrame(tk.Frame):
    def __init__(self, core, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.core = core
        self.label_title = tk.Label(self, text='Название плана', justify=tk.CENTER)
        self.entry_title = tk.Entry(self, font='bold', justify=tk.CENTER)
        self.button_load_plan = tk.Button(self, text='Загрузить план', justify=tk.CENTER, command=self.__load_plan)
        self.button_save_plan = tk.Button(self, text='Сохранить план', justify=tk.CENTER, command=self.__save_plan)
        
        self.top_panel = tk.Frame(self)
        self.frame_input_parameters = InputParametersFrame(self.top_panel)
        self.frame_parameters_ores = ParametersFrame(self.top_panel, headers=self.core['ore_types'], variants=PARAMETERS_1, text="Руды/Вскрыша")
        self.frame_parameters_components = ParametersFrame(self.top_panel, headers=self.core['component_types'], variants=PARAMETERS_2, text="Единицы измерения")
        self.frame_places_order = FlawingOrderFrame(self.top_panel)

        self.label_calendar = tk.Label(self, text=CALENDAR_HEADER, justify=tk.CENTER, relief=tk.RAISED, width=10)
        self.label_calendar_choosen = tk.Label(self, text='', justify=tk.CENTER, relief=tk.RIDGE, width=10)
        self.listbox_calendar = tk.Listbox(self, listvariable=(), selectmode=tk.SINGLE, height=TABLE_HEIGHT, justify=tk.CENTER, width=10)
        
        self.label_places = tk.Label(self, text=PLACE_HEADER, justify=tk.CENTER, relief=tk.RAISED, width=10)
        self.label_places_choosen = tk.Label(self, text='', justify=tk.CENTER, relief=tk.RIDGE, width=10)
        self.listbox_places = tk.Listbox(self, listvariable=(), selectmode=tk.SINGLE, height=TABLE_HEIGHT, justify=tk.CENTER, width=10)
        self.listbox_places['state'] = tk.DISABLED

        self.treeview_horizonts = ttk.Treeview(self, columns=self.core['component_types'], displaycolumns='#all', show='headings', height=TABLE_HEIGHT)
        self.__initialization_treeview()

        self.amount_of_component = AmountFrame(self, headers=self.core['component_types'], readonly=True, text='Средневзвешенное по плану')
        self.amount_of_ore = AmountFrame(self, headers=self.core['places'], text='Сумма горной массы по плану')
        #self.amount_of_horizonts = AmountFrame(self, headers=('Участок 1',), text='Максимум горизонтов')
        self.button_recalculate = ttk.Button(self, text='Рассчитать 1 период', command=self.__handler_calculate_one_period)
        self.checkbutton_fix_place = ttk.Checkbutton(self, text='Зафиксировать количество руды', command=self.__handler_fix_plan)
        self.button_calculate = ttk.Button(self, text='Рассчитать несколько периодов', command=self.__handler_calculate_few_periods)
        self.spinbox_calculate = ttk.Spinbox(self, from_=0, to=1000, command=self.__handler_spinbox_changed)
        self.button_clear_plan = ttk.Button(self, text='Начать рассчеты заново', command=self.__clear_plan)
        self.text_log = tk.Text(self, height=5)
        self.text_log['state'] = 'disabled'
        self._bind()
        self.core
        self._pack()

    def _bind(self):
        self.listbox_calendar.bind('<Double-Button-1>', self.__listbox_date_handler)
        self.listbox_places.bind('<Double-Button-1>', self.__listbox_place_handler)

    def _pack(self):
        self.columnconfigure(3, weight=1)
        self.rowconfigure(5, weight=1)

        self.top_panel.columnconfigure(1, weight=1)
        self.top_panel.rowconfigure(1, weight=1)
        self.frame_input_parameters.grid(           column=1, row=1, sticky=tk.NSEW)
        self.frame_parameters_ores.grid(            column=1, row=2, sticky=tk.NSEW)
        self.frame_parameters_components.grid(      column=1, row=3, sticky=tk.NSEW)
        self.frame_places_order.grid(               column=1, row=4, sticky=tk.NSEW)
        
        self.label_title.grid(                      column=1, row=0, columnspan=3, sticky=tk.NSEW)
        self.entry_title.grid(                      column=1, row=1, columnspan=3, sticky=tk.NSEW)
        self.button_load_plan.grid(                 column=4, row=0, columnspan=1, rowspan=2, sticky=tk.NSEW)
        self.button_save_plan.grid(                 column=5, row=0, columnspan=1, rowspan=2, sticky=tk.NSEW)
        self.top_panel.grid(                        column=1, row=2, columnspan=5, sticky=tk.NSEW)
        self.label_calendar.grid(                   column=1, row=3, sticky=tk.NSEW)
        self.label_places.grid(                     column=2, row=3, sticky=tk.NSEW)
        self.label_calendar_choosen.grid(           column=1, row=4, sticky=tk.NSEW)
        self.label_places_choosen.grid(             column=2, row=4, sticky=tk.NSEW)
        self.listbox_calendar.grid(                 column=1, row=5, sticky=tk.NSEW)
        self.listbox_places.grid(                   column=2, row=5, sticky=tk.NSEW)
        self.treeview_horizonts.grid(               column=3, row=3, columnspan=1, rowspan=3, sticky=tk.NSEW)
        self.amount_of_component.grid(              column=4, row=3, columnspan=1, rowspan=3, sticky=tk.NSEW)
        self.amount_of_ore.grid(                    column=5, row=3, columnspan=1, rowspan=3, sticky=tk.NSEW)
        #self.amount_of_horizonts.grid(              column=6, row=3, columnspan=1, rowspan=3, sticky=tk.NSEW)
        self.button_recalculate.grid(               column=1, row=6, columnspan=4, sticky=tk.NSEW)
        self.checkbutton_fix_place.grid(            column=5, row=6, columnspan=1, sticky=tk.NSEW)
        self.button_calculate.grid(                 column=1, row=7, columnspan=4, sticky=tk.NSEW)
        self.spinbox_calculate.grid(                column=5, row=7, columnspan=1, sticky=tk.NSEW)
        self.button_clear_plan.grid(                column=1, row=8, columnspan=5, sticky=tk.NSEW)
        self.text_log.grid(                         column=1, row=9, columnspan=5, sticky=tk.NSEW)

    def init(self):
        places = self.core['places']
        first_date = f'{dt.today().date()}'
        dates = {first_date: {}}
        for place in places:
            dates[first_date][place] = []
        self.core.set(dates=dates)

        self.listbox_places['state'] = tk.NORMAL
        self.listbox_places.delete(0, tk.END)
        for place in places:
            self.listbox_places.insert(tk.END, place)
        self.listbox_places['state'] = tk.DISABLED
        self.listbox_calendar.delete(0, tk.END)
        self.listbox_calendar.insert(tk.END, first_date)

        self.__set_headers()
        self.__parameters_from_core()
        self._pack()

    def __listbox_date_handler(self, event):
        cursor = self.listbox_calendar.selection_get()
        self.label_calendar_choosen['text'] = cursor
        self.listbox_places['state'] = tk.NORMAL
        self.treeview_horizonts.delete(*self.treeview_horizonts.get_children())

    def __listbox_place_handler(self, event):
        # self.button_recalculate['state'] = tk.NORMAL
        # self.checkbutton_fix_place['state'] = tk.NORMAL
        cursor = self.listbox_places.selection_get()
        self.label_places_choosen['text'] = cursor
        date = self.label_calendar_choosen['text']
        place = cursor
        self.treeview_horizonts.delete(*self.treeview_horizonts.get_children())
        plan = self.core['plan'][date][place]
        summ_of_components = [0] * len(self.core['component_types'])
        mass = 0
        for row in plan:
            row = list(row)
            mass += row[3]
            for i, density in enumerate(row[4:]):
                summ_of_components[i] += row[3] * row[4+i]
            for i, value in enumerate(row):
                if 1 < i < 4:
                    row[i] = int(value)
                elif i == 4:
                    row[i] = round(value, 6)
                elif i > 4:
                    row[i] = round(value, 3)        
            self.__treeview_append(row)
        for i, component in enumerate(summ_of_components):
            summ_of_components[i] = component / mass if mass != 0 else 0
        self.amount_of_component.set_values(summ_of_components)

    def __handler_calculate_one_period(self):
        self.__parameters_to_core()
        self.__set_frame_state(tk.DISABLED)
        if self.checkbutton_fix_place.instate(('active',)):
            amount = self.amount_of_ore.get_values()
            for i, place in enumerate(self.core['places']):
                self.core['plan_modify'][place] = amount[i]
            self.core.compute()

    def __handler_calculate_few_periods(self):
        self.__parameters_to_core()
        try:
            proc = self.core.compute()
            while (output := next(proc)) != None:
                self.__set_log(output)
                self.update()
            components = self.core['component_types']
            self.frame_parameters_components.edit_headers(components)
            self.amount_of_component.edit_headers(components)
            self.frame_input_parameters.edit_components(components)
            self.__plan_from_core()
            self.update()
        finally:
            self.__set_frame_state(tk.NORMAL)

    def __clear_plan(self):
        self.core.clear_plan()
        self.init()

    def __load_plan(self):
        self.__set_frame_state(tk.DISABLED)
        try:
            filename = fd.askopenfilename(defaultextension='.pklcore', filetypes=[('Serialized Core','*.pklcore'),
                                                                                ('All files', '*')])
            self.core.serializer('LOAD', filename)
            self.init()
            self.__parameters_from_core()
            self.__plan_from_core()
        except Exception as e:
            self.__set_log(f'{type(e)}\n{e}')
            raise e
        finally:
            self.__set_frame_state(tk.NORMAL)

    def __save_plan(self):
        self.__set_frame_state(tk.DISABLED)
        try:
            filename = fd.asksaveasfilename(defaultextension='.pklcore', filetypes=[('Serialized Core','*.pklcore'),
                                                                                ('All files', '*')])
            self.__parameters_to_core()
            self.core.serializer(mode='SAVE', name=filename)
        except Exception as e:
            self.__set_log(f'{type(e)}: {e}')
        self.__set_frame_state(tk.NORMAL)

    def __parameters_to_core(self):
        self.core.data['namespace'] = self.entry_title.get()
        parameters = self.frame_input_parameters.get_parameters()
        parameters['usefull_ores'] = self.frame_parameters_ores.get_all()
        parameters['measure_count'] = self.frame_parameters_components.get_all()
        self.core['places'] = self.frame_places_order.get_order()
        self.core['parameters'] = parameters

    def __parameters_from_core(self):
        params = self.core['parameters']
        self.frame_input_parameters.set_parameters(**params)
        self.frame_parameters_ores.set_all(params['usefull_ores'])
        self.frame_parameters_components.set_all(params['measure_count'])

    def __plan_from_core(self):
        self.listbox_calendar.delete(0, tk.END)
        for date in self.core['plan']:
            self.listbox_calendar.insert(tk.END, date)
    
    def __set_headers(self):
        career_name, places, ore_types, components = self.core.get_headers()
        self.entry_title.delete(0, tk.END)
        self.entry_title.insert(0, career_name)
        self.frame_parameters_components.set_headers(components)
        self.frame_parameters_ores.set_headers(ore_types)
        self.__initialization_treeview()
        self.amount_of_component.set_headers(components)
        self.amount_of_ore.set_headers(places)
        self.frame_input_parameters.set_places(list(places))
        self.frame_input_parameters.set_components(components)
        self.frame_places_order.set_objects(places)


    def __set_frame_state(self, state):
        self.spinbox_calculate['state'] = state
        self.checkbutton_fix_place['state'] = state
        self.button_recalculate['state'] = state
        self.button_calculate['state'] = state
        self.button_load_plan['state'] = state
        self.button_save_plan['state'] = state

    def __set_log(self, text):
        self.text_log['state'] = tk.NORMAL
        self.text_log.delete(0.0, tk.END)
        self.text_log.insert(0.0, text)
        self.text_log['state'] = tk.DISABLED

    def __initialization_treeview(self):
        components = self.core['component_types']
        self.treeview_horizonts['columns'] = CARREER_HORIZONTS + tuple(components)
        for i, (text, width) in enumerate(CARREER_HORIZONTS):
            self.treeview_horizonts.heading(i, text=text)
            self.treeview_horizonts.column(i, minwidth=width, width=width)
        for i in range(len(components)):
            width = 430 // len(components)
            self.treeview_horizonts.heading(i+len(CARREER_HORIZONTS), text=components[i])
            self.treeview_horizonts.column(i+len(CARREER_HORIZONTS), minwidth=width, width=width)

    def __treeview_append(self, item):
        self.treeview_horizonts.insert("", tk.END, values=item)

    def __start_calculation(self):
        self.listbox_calendar.delete(0, tk.END)
        # self.button_recalculate['state'] = tk.DISABLED
        # self.checkbutton_fix_place['state'] = tk.DISABLED
        self.label_calendar_choosen['text'] = ''
        self.label_places_choosen['text'] = ''
        self.__set_frame_state(tk.DISABLED)
        self.__parameters_to_core()

    def __end_calculation(self):
        pass