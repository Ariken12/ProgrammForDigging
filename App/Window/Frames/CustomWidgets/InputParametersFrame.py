import tkinter as tk
from tkinter import ttk
from datetime import datetime as dt

class InputParametersFrame(ttk.LabelFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self['text'] = 'Ввод параметров'
        self.label_acceleration = tk.Label(self, text="Разгон добычи")
        self.spinbox_acceleration = ttk.Spinbox(self, from_=1, to=5, increment=1, 
                                               command=self.__spinbox_acceleration_handler, width=10)
        self.spinbox_acceleration.set(1)
        self.label_speed = tk.Label(self, text="Скорость\nдобычи")
        self.labels_acceleration = []
        self.entrys_acceleration = []
        
        self.label_max_depth = tk.Label(self, text='Макс. кол-во\nуступов для участка')
        self.labels_max_depth = []
        self.entrys_max_depth = []

        self.label_components = tk.Label(self, text='Содержание компонентов')
        self.labels_components = []
        self.entrys_components = []

        first_date = f'{dt.today().date()}'
        
        self.label_started_date = tk.Label(self, text='Дата начала')
        self.entry_started_date = tk.Entry(self)
        self.entry_started_date.insert(0, first_date)

        self.label_precision_date = tk.Label(self, text='Дробность периодов')
        self.list_precision_date = ['Год', 'Полугодие', 'Квартал', 'Месяц', 'Неделя']
        self.combobox_precision_date = ttk.Combobox(self, values=self.list_precision_date)
        self.combobox_precision_date.set(self.list_precision_date[0])

        self.label_precision_value = tk.Label(self, text='Рассчет коэффициента')
        self.list_precision_value = ['M / M', 'V / M', 'V / V']
        self.combobox_precision_value = ttk.Combobox(self, values=self.list_precision_value)
        self.combobox_precision_value.set(self.list_precision_value[0])
        
        self.label_k_lim = tk.Label(self, text='Максимальный K вскрыши')
        self.entry_k_lim = tk.Entry(self)
        self.entry_k_lim.insert(0, 1000)

        self.__spinbox_acceleration_handler()
        
        self._pack()

    def _pack(self):
        self.grid_columnconfigure(20, weight=1)
        self.label_acceleration.grid(           column=1, row=1, sticky=tk.NSEW)
        self.spinbox_acceleration.grid(         column=1, row=2, sticky=tk.NSEW)
        self.label_speed.grid(                  column=2, row=1, rowspan=2, sticky=tk.NSEW)
        for i, label in enumerate(self.labels_acceleration):
            label.grid(                         column=3+i, row=1, sticky=tk.NSEW)
        for i, entry in enumerate(self.entrys_acceleration):
            entry.grid(                         column=3+i, row=2, sticky=tk.NSEW)

        self.label_max_depth.grid(              column=1, row=3, rowspan=2, columnspan=2, sticky=tk.NSEW)
        for i, label in enumerate(self.labels_max_depth):
            label.grid(                         column=3+i, row=3, sticky=tk.NSEW)
        for i, entry in enumerate(self.entrys_max_depth):
            entry.grid(                         column=3+i, row=4, sticky=tk.NSEW)
        
        self.label_components.grid(             column=1, row=5, rowspan=2, columnspan=2, sticky=tk.NSEW)
        for i, label in enumerate(self.labels_components):
            label.grid(                         column=3+i, row=5, sticky=tk.NSEW)
        for i, entry in enumerate(self.entrys_components):
            entry.grid(                         column=3+i, row=6, sticky=tk.NSEW)

        self.label_started_date.grid(           column=21, row=1, sticky=tk.NSEW)
        self.entry_started_date.grid(           column=22, row=1, sticky=tk.NSEW)
        
        self.label_precision_date.grid(         column=21, row=2, sticky=tk.NSEW)
        self.combobox_precision_date.grid(      column=22, row=2, sticky=tk.NSEW)
        
        self.label_precision_value.grid(        column=21, row=3, sticky=tk.NSEW)
        self.combobox_precision_value.grid(     column=22, row=3, sticky=tk.NSEW)
        
        self.label_k_lim.grid(                  column=21, row=4, sticky=tk.NSEW)
        self.entry_k_lim.grid(                  column=22, row=4, sticky=tk.NSEW)

    
    def __spinbox_acceleration_handler(self):
        num_of_years = self.spinbox_acceleration.get()
        for widget in self.labels_acceleration + self.entrys_acceleration:
            widget.destroy()
        self.labels_acceleration.clear()
        self.entrys_acceleration.clear()
        for i in range(int(num_of_years)):
            self.labels_acceleration.append(tk.Label(self, text=f'Год {i+1}'))
            self.entrys_acceleration.append(tk.Entry(self, width=10))
        self._pack()
        
    def set_places(self, places):
        num_of_places = len(places)
        for widget in self.labels_max_depth + self.entrys_max_depth:
            widget.destroy()
        self.labels_max_depth.clear()
        self.entrys_max_depth.clear()
        for i in range(num_of_places):
            self.labels_max_depth.append(tk.Label(self, text=places[i]))
            self.entrys_max_depth.append(tk.Entry(self, width=10))
            self.entrys_max_depth[-1].insert(0, '0')
        self._pack()

    def set_components(self, components):
        num_of_components = len(components)
        for widget in self.labels_components + self.entrys_components:
            widget.destroy()
        self.labels_components.clear()
        self.entrys_components.clear()
        for i in range(num_of_components):
            self.labels_components.append(tk.Label(self, text=components[i]))
            self.entrys_components.append(tk.Entry(self, width=10))
            self.entrys_components[-1].insert(0, '0')
        self._pack()

    def get_parameters(self):
        output = {}
        output['acceleration'] = []
        for entry in self.entrys_acceleration:
            output['acceleration'].append(float(entry.get()))
        output['max_dh'] = {}
        for i, entry in enumerate(self.entrys_max_depth):
            value = entry.get()
            if value == '':
                value = 0
            output['max_dh'][self.labels_max_depth[i]['text']] = float(value)
        output['components_lim'] = []
        for entry in self.entrys_components:
            value = entry.get()
            if value == '':
                value = 0
            output['components_lim'].append(float(value))
        output['begin_date'] = self.entry_started_date.get()
        output['step_date'] = self.combobox_precision_date.get()
        output['k_func'] = self.combobox_precision_value.get()
        return output