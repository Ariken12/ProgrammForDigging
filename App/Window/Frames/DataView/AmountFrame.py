import tkinter as tk
from tkinter import ttk


class AmountFrame(ttk.Labelframe):
    def __init__(self, *args, headers=(), **kwargs):
        super().__init__(*args, **kwargs)
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
            self.entryes.append(tk.Entry(self, justify=tk.LEFT))
        self._pack()

    def set_values(self, values):
        for i, value in enumerate(values):
            self.entryes[i].delete(0, tk.END)
            self.entryes[i].insert(str(value))