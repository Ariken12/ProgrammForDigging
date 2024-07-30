import tkinter as tk
from tkinter import ttk
import sys

from Window.Frames.DataView.Constants import *
from Window.Frames.DataView.ParametersFrame import ParametersFrame
from Window.Frames.DataView.AmountFrame import AmountFrame



class DataView(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ore_types = []
        self.label_carrier_name = tk.Label(self, text='Название карьера', font='Arial 20', justify=tk.CENTER)
        self.top_panel = tk.Frame(self)
        self.frame_parameters_ores = ParametersFrame(self.top_panel, headers=self.ore_types, variants=PARAMETERS_1, text="Руды/Вскрыша")
        self.frame_parameters_components = ParametersFrame(self.top_panel, headers=COMPONENTS, variants=PARAMETERS_2, text="Единицы измерения")
        
        self.calculate_button = tk.Button(self.top_panel, text='Рассчитать Значения', command=self.calculation_run)

        self.label_calendar = tk.Label(self, text='Год', justify=tk.CENTER, relief=tk.RAISED)
        self.listbox_calendar = tk.Listbox(self, listvariable=(), selectmode=tk.SINGLE, height=TABLE_HEIGHT)
        
        self.label_places = tk.Label(self, text='Участок', justify=tk.CENTER, relief=tk.RAISED)
        self.listbox_places = tk.Listbox(self, listvariable=(), selectmode=tk.SINGLE, height=TABLE_HEIGHT)

        self.treeview_horizonts = ttk.Treeview(self, columns=CARREER_HORIZONTS, displaycolumns='#all', show='headings', height=TABLE_HEIGHT)
        self._initialization_treeview(self.treeview_horizonts, CARREER_HORIZONTS)

        self.amount_of_component = AmountFrame(self, headers=COMPONENTS, text='Сумма компонентов на участке')
        self.amount_of_ore = AmountFrame(self, headers=self.ore_types, text='Сумма руды на участке')
        self._pack()

    def _pack(self):
        self.frame_parameters_ores.grid(            column=1, row=1, sticky=tk.NSEW)
        self.frame_parameters_components.grid(      column=2, row=1, sticky=tk.NSEW)
        self.calculate_button.grid(                 column=3, row=1, sticky=tk.EW)
        self.label_carrier_name.grid(               column=1, row=1, columnspan=7, sticky=tk.NSEW)
        self.top_panel.grid(                        column=1, row=2, columnspan=7, sticky=tk.NSEW)
        self.label_calendar.grid(                   column=1, row=3, sticky=tk.NSEW)
        self.label_places.grid(                     column=2, row=3, sticky=tk.NSEW)
        self.listbox_calendar.grid(                 column=1, row=4, sticky=tk.NSEW)
        self.listbox_places.grid(                   column=2, row=4, sticky=tk.NSEW)
        self.treeview_horizonts.grid(               column=3, row=3, columnspan=3, rowspan=2, sticky=tk.NSEW)
        self.amount_of_component.grid(            column=6, row=3, columnspan=1, rowspan=2, sticky=tk.NS)
        self.amount_of_ore.grid(           column=7, row=3, columnspan=1, rowspan=2, sticky=tk.NS)

    def _initialization_treeview(self, treeview: ttk.Treeview, init_list: list[tuple[str, int]]):
        for i in range(len(init_list)):
            treeview.heading(i, text=init_list[i][0])
            treeview.column(i, minwidth=init_list[i][1], width=init_list[i][1])

    def init(self, career_name: str='Карьер', ore_types: tuple[str]=()):
        self.label_carrier_name['text'] = career_name
        self.frame_parameters_ores.set_headers(ore_types)
        self.amount_of_ore.set_headers(ore_types)
        self._pack()

    def calculation_run(self):
        pass