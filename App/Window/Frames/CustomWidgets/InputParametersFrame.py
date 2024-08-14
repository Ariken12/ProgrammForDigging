import tkinter as tk
from tkinter import ttk


class InputParametersFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_acceleration = tk.Label(self, text="Разгон добычи")
        self.spinbox_acceleration = ttk.Spinbox(self, from_=1, to=5, increment=1, 
                                               command=self.__spinbox_acceleration_handler, width=10)
        self.label_speed = tk.Label(self, text="Скорость добычи")
        self.labels_acceleration = []
        self.entrys_acceleration = []
        
        self.label_max_depth = tk.Label(self, text='Макс. кол-во уступов для участка')
        self.labels_max_depth = []
        self.entrys_max_depth = []

        self.label_components = tk.Label(self, text='Содержание компонентов')
        self.labels_components = []
        self.entrys_components = []

        self.label_started_date = tk.Label(self, text='Дата начала')
        self.entry_started_date = tk.Entry(self)

        self.label_precision_date = tk.Label(self, text='Дробность периодов')
        self.list_precision_date = ['Год', 'Полугодие', 'Сезон', 'Месяц', 'Неделя']
        self.combobox_precision_date = ttk.Combobox(self, values=self.list_precision_date)

        self.label_precision_value = tk.Label(self, text='Рассчет коэффициента')
        self.list_precision_value = ['M / M', 'V / M', 'V / V']
        self.combobox_precision_value = ttk.Combobox(self, values=self.list_precision_value)
        
        self._pack()

    def _pack(self):

        self.label_acceleration.grid(           column=1, row=1, sticky=tk.NSEW)
        self.spinbox_acceleration.grid(         column=1, row=2, sticky=tk.NSEW)
        self.label_speed.grid(                  column=2, row=1, rowspan=2, sticky=tk.NSEW)
        for i, label in enumerate(self.labels_acceleration):
            label.grid(                         column=3+i, row=1, sticky=tk.NSEW)
        for i, entry in enumerate(self.entrys_acceleration):
            entry.grid(                         column=3+i, row=2, sticky=tk.NSEW)

    
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
            self.entrys_max_depth.append(tk.Entry(self))

    def set_components(self, components):
        num_of_components = len(components)
        for widget in self.labels_components + self.entrys_components:
            widget.destroy()
        self.labels_components.clear()
        self.entrys_components.clear()
        for i in range(num_of_components):
            self.labels_components.append(tk.Label(self, text=components[i]))
            self.entrys_components.append(tk.Entry(self))