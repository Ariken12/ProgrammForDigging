import tkinter as tk
from tkinter import ttk
import sys
from datetime import datetime as dt

from Window.Frames.DataView.Constants import *
from Window.Frames.DataView.ParametersFrame import ParametersFrame
from Window.Frames.DataView.AmountFrame import AmountFrame


class DataView(tk.Frame):
    def __init__(self, core, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.core = core
        self.ore_types = []
        self.label_carrier_name = tk.Label(self, text='Название карьера', font='Arial 20', justify=tk.CENTER)
        self.top_panel = tk.Frame(self)
        self.frame_parameters_ores = ParametersFrame(self.top_panel, headers=self.ore_types, variants=PARAMETERS_1, text="Руды/Вскрыша")
        self.frame_parameters_components = ParametersFrame(self.top_panel, headers=COMPONENTS, variants=PARAMETERS_2, text="Единицы измерения")
        
        self.label_calendar = tk.Label(self, text=CALENDAR_HEADER, justify=tk.CENTER, relief=tk.RAISED, width=10)
        self.label_calendar_choosen = tk.Label(self, text='', justify=tk.CENTER, relief=tk.RIDGE, width=10)
        self.listbox_calendar = tk.Listbox(self, listvariable=(), selectmode=tk.SINGLE, height=TABLE_HEIGHT, justify=tk.CENTER)
        
        self.label_places = tk.Label(self, text=PLACE_HEADER, justify=tk.CENTER, relief=tk.RAISED, width=10)
        self.label_places_choosen = tk.Label(self, text='', justify=tk.CENTER, relief=tk.RIDGE, width=10)
        self.listbox_places = tk.Listbox(self, listvariable=(), selectmode=tk.SINGLE, height=TABLE_HEIGHT, justify=tk.CENTER)
        self.listbox_places['state'] = tk.DISABLED

        self.treeview_horizonts = ttk.Treeview(self, columns=CARREER_HORIZONTS, displaycolumns='#all', show='headings', height=TABLE_HEIGHT)
        self._initialization_treeview(self.treeview_horizonts, CARREER_HORIZONTS)

        self.amount_of_component = AmountFrame(self, headers=COMPONENTS, readonly=True, text='Сумма компонентов по плану')
        self.amount_of_ore = AmountFrame(self, headers=self.ore_types, text='Сумма руды по плану')
        self.button_recalculate = tk.Button(self, text='Пересчитать значения', command=self._recalculate_values)
        self.button_calculate = tk.Button(self, text='Рассчитать Значения', command=self.calculation_run)
        self.button_recalculate['state'] = tk.DISABLED
        self._bind()
        self._pack()

    def _bind(self):
        self.listbox_calendar.bind('<Double-Button-1>', self._listbox_date_handler)
        self.listbox_places.bind('<Double-Button-1>', self._listbox_place_handler)

    def _pack(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(5, weight=1)
        self.top_panel.columnconfigure(1, weight=1)
        self.top_panel.columnconfigure(2, weight=1)
        self.frame_parameters_ores.grid(            column=1, row=1, sticky=tk.NSEW)
        self.frame_parameters_components.grid(      column=2, row=1, sticky=tk.NSEW)
        self.label_carrier_name.grid(               column=1, row=1, columnspan=7, sticky=tk.NSEW)
        self.top_panel.grid(                        column=1, row=2, columnspan=7, sticky=tk.NSEW)
        self.label_calendar.grid(                   column=1, row=3, sticky=tk.NSEW)
        self.label_places.grid(                     column=2, row=3, sticky=tk.NSEW)
        self.label_calendar_choosen.grid(           column=1, row=4, sticky=tk.NSEW)
        self.label_places_choosen.grid(             column=2, row=4, sticky=tk.NSEW)
        self.listbox_calendar.grid(                 column=1, row=5, sticky=tk.NSEW)
        self.listbox_places.grid(                   column=2, row=5, sticky=tk.NSEW)
        self.treeview_horizonts.grid(               column=3, row=3, columnspan=1, rowspan=3, sticky=tk.NSEW)
        self.amount_of_component.grid(              column=4, row=3, columnspan=1, rowspan=3, sticky=tk.NS)
        self.amount_of_ore.grid(                    column=5, row=3, columnspan=1, rowspan=3, sticky=tk.NS)
        self.button_recalculate.grid(               column=1, row=6, columnspan=7, sticky=tk.EW)
        self.button_calculate.grid(                 column=1, row=7, columnspan=7, sticky=tk.EW)

    def _listbox_date_handler(self, event):
        cursor = self.listbox_calendar.selection_get()
        self.label_calendar_choosen['text'] = cursor
        self.listbox_places['state'] = tk.NORMAL
        print(cursor)

    def _listbox_place_handler(self, event):
        self.button_recalculate['state'] = tk.NORMAL
        cursor = self.listbox_places.selection_get()
        self.label_places_choosen['text'] = cursor
        date = self.label_calendar_choosen['text']
        place = cursor
        self.treeview_horizonts.delete(*self.treeview_horizonts.get_children())
        plan = self.core[date][place]
        for item in plan:
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

    def _initialization_treeview(self, treeview: ttk.Treeview, init_list: list[tuple[str, int]]):
        for i in range(len(init_list)):
            treeview.heading(i, text=init_list[i][0])
            treeview.column(i, minwidth=init_list[i][1], width=init_list[i][1])

    def _treeview_append(self, item):
        self.treeview_horizonts.insert("", tk.END, values=item)

    def init(self):
        career_name, places, ore_types = self.core.data_get_meta()

        self.label_carrier_name['text'] = career_name
        self.frame_parameters_ores.set_headers(ore_types)
        self.amount_of_ore.set_headers(ore_types)

        first_date = f'{dt.today().date()}'
        dates = {first_date: {}}
        for place in places:
            dates[first_date][place] = []
        self.core.set(dates=dates)

        self.listbox_places['state'] = tk.NORMAL
        for place in places:
            self.listbox_places.insert(tk.END, place)
        self.listbox_places['state'] = tk.DISABLED
        self.listbox_calendar.insert(tk.END, first_date)
        self._pack()

    def calculation_run(self):
        pass