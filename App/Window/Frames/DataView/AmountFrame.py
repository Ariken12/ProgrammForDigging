import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tkmb


class AmountFrame(ttk.Labelframe):
    def __init__(self, *args, headers=(), readonly=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.readonly = readonly
        self.list_of_ores = headers
        self.labeles = []
        self.entryes = []
        self.set_headers(headers)
        self._pack()

    def _pack(self):
        for i, label in enumerate(self.labeles):
            label.grid(column=1, row=i, sticky=tk.NSEW)
            self.entryes[i].grid(column=2, row=i, sticky=tk.NSEW)

    def set_headers(self, headers):
        self.list_of_ores = headers
        for ore in headers:
            self.labeles.append(tk.Label(self, text=ore, justify=tk.RIGHT))
            self.entryes.append(tk.Entry(self, justify=tk.LEFT, state='readonly' if self.readonly else 'normal'))
        self._pack()

    def set_values(self, values):
        for i, value in enumerate(values):
            if self.readonly:
                self.entryes[i]['state'] = 'normal'
            self.entryes[i].delete(0, tk.END)
            self.entryes[i].insert(0, str(value))
            if self.readonly:
                self.entryes[i]['state'] = 'readonly'

    def get_values(self):
        result = []
        for entry in self.entryes:
            value = entry.get()
            if value == '':
                result.append(0)
                continue
            result.append(float(value))
        return tuple(result)