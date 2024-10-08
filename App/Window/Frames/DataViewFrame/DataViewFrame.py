import tkinter as tk
import tkinter.filedialog as fd
from tkinter import ttk
import sys
from datetime import datetime as dt
import numpy as np


from Window.Frames.DataViewFrame.Constants import *
from Window.Frames.CustomWidgets.ParametersFrame import ParametersFrame
from Window.Frames.CustomWidgets.AmountFrame import AmountFrame
from Window.Frames.CustomWidgets.InputParametersFrame import InputParametersFrame


class DataViewFrame(tk.Frame):
    def __init__(self, core, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.core = core
        self.label_title = tk.Label(self, text='Название плана', justify=tk.CENTER)
        self.entry_title = tk.Entry(self, font='bold', justify=tk.CENTER)
        self.button_load_plan = tk.Button(self, text='Загрузить план', justify=tk.CENTER, command=self.__load_plan)
        self.button_save_plan = tk.Button(self, text='Сохранить план', justify=tk.CENTER, command=self.__save_plan)
        
        self.ore_types = []
        self.top_panel = tk.Frame(self)
        self.frame_input_parameters = InputParametersFrame(self.top_panel)
        self.frame_parameters_ores = ParametersFrame(self.top_panel, headers=self.ore_types, variants=PARAMETERS_1, text="Руды/Вскрыша")
        self.frame_parameters_components = ParametersFrame(self.top_panel, headers=self.core.data.components_types, variants=PARAMETERS_2, text="Единицы измерения")
        
        self.label_calendar = tk.Label(self, text=CALENDAR_HEADER, justify=tk.CENTER, relief=tk.RAISED, width=10)
        self.label_calendar_choosen = tk.Label(self, text='', justify=tk.CENTER, relief=tk.RIDGE, width=10)
        self.listbox_calendar = tk.Listbox(self, listvariable=(), selectmode=tk.SINGLE, height=TABLE_HEIGHT, justify=tk.CENTER, width=10)
        
        self.label_places = tk.Label(self, text=PLACE_HEADER, justify=tk.CENTER, relief=tk.RAISED, width=10)
        self.label_places_choosen = tk.Label(self, text='', justify=tk.CENTER, relief=tk.RIDGE, width=10)
        self.listbox_places = tk.Listbox(self, listvariable=(), selectmode=tk.SINGLE, height=TABLE_HEIGHT, justify=tk.CENTER, width=10)
        self.listbox_places['state'] = tk.DISABLED

        self.treeview_horizonts = ttk.Treeview(self, columns=self.core.data.components_types, displaycolumns='#all', show='headings', height=TABLE_HEIGHT)
        self._initialization_treeview()

        self.amount_of_component = AmountFrame(self, headers=self.core.data.components_types, readonly=True, text='Средневзвешенное по плану')
        self.amount_of_ore = AmountFrame(self, headers=self.ore_types, text='Сумма руды по плану')
        #self.amount_of_horizonts = AmountFrame(self, headers=('Участок 1',), text='Максимум горизонтов')
        self.button_recalculate = tk.Button(self, text='Пересчитать участок', command=self._recalculate_values)
        self.variable_fix_place = tk.BooleanVar()
        self.checkbutton_fix_place = tk.Checkbutton(self, text='Зафиксировать участок', variable=self.variable_fix_place)
        self.button_calculate = tk.Button(self, text='Рассчитать план', command=self.calculation_run)
        self.button_recalculate['state'] = tk.DISABLED
        self.text_log = tk.Text(self, height=5)
        self.text_log['state'] = 'disabled'
        self._bind()
        self._pack()

    def _bind(self):
        self.listbox_calendar.bind('<Double-Button-1>', self._listbox_date_handler)
        self.listbox_places.bind('<Double-Button-1>', self._listbox_place_handler)

    def _pack(self):
        self.columnconfigure(3, weight=1)
        self.rowconfigure(5, weight=1)

        self.top_panel.columnconfigure(1, weight=1)
        self.top_panel.rowconfigure(1, weight=1)
        self.frame_input_parameters.grid(           column=1, row=1, sticky=tk.NSEW)
        self.frame_parameters_ores.grid(            column=1, row=2, sticky=tk.NSEW)
        self.frame_parameters_components.grid(      column=1, row=3, sticky=tk.NSEW)
        
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
        self.button_recalculate.grid(               column=1, row=6, columnspan=5, sticky=tk.NSEW)
        self.checkbutton_fix_place.grid(            column=5, row=6, columnspan=1, sticky=tk.NSEW)
        self.button_calculate.grid(                 column=1, row=7, columnspan=5, sticky=tk.NSEW)
        self.text_log.grid(                         column=1, row=8, columnspan=5, sticky=tk.NSEW)

    def _listbox_date_handler(self, event):
        cursor = self.listbox_calendar.selection_get()
        self.label_calendar_choosen['text'] = cursor
        self.listbox_places['state'] = tk.NORMAL
        self.treeview_horizonts.delete(*self.treeview_horizonts.get_children())

    def _listbox_place_handler(self, event):
        self.button_recalculate['state'] = tk.NORMAL
        cursor = self.listbox_places.selection_get()
        self.label_places_choosen['text'] = cursor
        date = self.label_calendar_choosen['text']
        place = cursor
        self.treeview_horizonts.delete(*self.treeview_horizonts.get_children())
        plan = self.core[date][place]
        for item in plan:
            item = list(item)
            for i, value in enumerate(item):
                if 1 < i < 4:
                    item[i] = int(value)
                elif i == 4:
                    item[i] = round(value, 6)
                elif i > 4:
                    item[i] = round(value, 3)
            self._treeview_append(item)

    def _recalculate_values(self):
        date = self.label_calendar_choosen['text']
        place = self.label_places_choosen['text']
        values = self.amount_of_ore.get_values()
        self.core.set(resources={date: {place: values}})
        self.core.recalculate()
        plan = self.core[date][place]
        self.treeview_horizonts.delete(*self.treeview_horizonts.get_children())
        for item in plan:
            self._treeview_append(item)
        self.amount_of_component.set_values(self.core.data.components[date][place])

    def _initialization_treeview(self):
        components = self.core.data.components_types
        self.treeview_horizonts['columns'] = CARREER_HORIZONTS + tuple(components)
        for i, (text, width) in enumerate(CARREER_HORIZONTS):
            self.treeview_horizonts.heading(i, text=text)
            self.treeview_horizonts.column(i, minwidth=width, width=width)
        for i in range(len(components)):
            width = 430 // len(components)
            self.treeview_horizonts.heading(i+len(CARREER_HORIZONTS), text=components[i])
            self.treeview_horizonts.column(i+len(CARREER_HORIZONTS), minwidth=width, width=width)

    def _treeview_append(self, item):
        self.treeview_horizonts.insert("", tk.END, values=item)

    def init(self):
        career_name, places, ore_types = self.core.data_get_meta()
        components = self.core.data.components_types

        self.entry_title.delete(0, tk.END)
        self.entry_title.insert(0, career_name)

        self.amount_of_component.set_headers(components)
        self.frame_parameters_components.set_headers(components)

        self._initialization_treeview()

        self.frame_parameters_ores.set_headers(ore_types)
        self.amount_of_ore.set_headers(ore_types)
        # self.amount_of_horizonts.set_headers(places)

        self.frame_input_parameters.set_places(list(places))
        self.frame_input_parameters.set_components(components)

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
        self._pack()

    def calculation_run(self):
        self.listbox_calendar.delete(0, tk.END)
        self.set_frame_state(tk.DISABLED)
        self.__parameters_to_core()
        try:
            proc = self.core.start()
            while (output := next(proc)) != None:
                self.set_log(output)
                self.update()
            self.__plan_from_core()
        finally:
            self.set_frame_state(tk.NORMAL)

    def __load_plan(self):
        self.set_frame_state(tk.DISABLED)
        try:
            filename = fd.askopenfilename(defaultextension='.pklcore', filetypes=[('Serialized Core','*.pklcore'),
                                                                                ('All files', '*')])
            self.core.serializer('LOAD', filename)
            self.init()
            self.__parameters_from_core()
            self.__plan_from_core()
        except Exception as e:
            self.set_log(f'{type(e)}\n{e}')
            raise e
        finally:
            self.set_frame_state(tk.NORMAL)


    def __save_plan(self):
        self.set_frame_state(tk.DISABLED)
        try:
            filename = fd.asksaveasfilename(defaultextension='.pklcore', filetypes=[('Serialized Core','*.pklcore'),
                                                                                ('All files', '*')])
            self.__parameters_to_core()
            self.core.serializer(mode='SAVE', name=filename)
        except Exception as e:
            self.set_log(f'{type(e)}: {e}')
        self.set_frame_state(tk.NORMAL)

    def __parameters_to_core(self):
        self.core.data.name_space = self.entry_title.get()
        parameters = self.frame_input_parameters.get_parameters()
        parameters['usefull_ores'] = self.frame_parameters_ores.get_all()
        parameters['measure_count'] = self.frame_parameters_components.get_all()
        self.core.set(parameters=parameters)

    def __parameters_from_core(self):
        params = self.core.data.parameters
        self.frame_input_parameters.set_parameters(**params)
        self.frame_parameters_ores.set_all(params['usefull_ores'])
        self.frame_parameters_components.set_all(params['measure_count'])

    def __plan_from_core(self):
        for date in self.core.data.plan:
            self.listbox_calendar.insert(tk.END, date)

    def set_frame_state(self, state):
        self.button_calculate['state'] = state
        self.button_load_plan['state'] = state
        self.button_save_plan['state'] = state

    def set_log(self, text):
        self.text_log['state'] = tk.NORMAL
        self.text_log.delete(0.0, tk.END)
        self.text_log.insert(0.0, text)
        self.text_log['state'] = tk.DISABLED
