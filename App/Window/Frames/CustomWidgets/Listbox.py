import tkinter as tk
from tkinter import ttk


class Listbox(tk.Frame):
    def __init__(self, *args, header, listvariable, height, label_style='Inverse.TLabel', buttons_style='primary.Toolbutton', **kwargs):
        super().__init__(*args, **kwargs)
        self.label = ttk.Label(self, text=header, style=label_style)
        self.values = []
        self.values.extend(listvariable)
        self.variable = tk.StringVar(self)
        self.iend = 0
        self.radiobuttons = []
        for i in range(height):
            if height < len(listvariable):
                text=listvariable[i]
            else:
                text=''
            radiobutton = ttk.Radiobutton(self, text=text, value=text, variable=self.variable, style=buttons_style)
            self.radiobuttons.append(radiobutton)
        self._pack()

    def _pack(self):
        self.label.grid(column=1, row=1, sticky=tk.NSEW)
        for i, radiobutton in enumerate(self.radiobuttons):
            radiobutton.grid(column=1, row=2+i, sticky=tk.NSEW)

    def insert(self, index, value):
        if index == tk.END:
            index = self.iend
            self.iend += 1
        self.radiobuttons[index]['text'] = value

    def disable(self):
        pass

    def enable(self):
        pass