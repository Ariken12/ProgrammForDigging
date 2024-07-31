import tkinter as tk
from tkinter import ttk


class ParametersFrame(ttk.Labelframe):
    def __init__(self, *args, headers=(), variants=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.variants = variants
        self.headers = headers
        self.label_variants = []
        self.label_headers = []
        self.variables = []
        self.radiobuttons = []
        self.__init_label_variants()
        self.__init_label_headers()
        self.__init_variables()
        self.__init_radiobuttons()
        self._pack()

    def _pack(self):
        for i, label in enumerate(self.label_variants):
            label.grid(column=1, row=1+i, sticky=tk.NSEW)
        for i, label in enumerate(self.label_headers):
            self.columnconfigure(2+i, weight=1)
            label.grid(column=2+i, row=1, sticky=tk.NSEW)
        for i, radiobuttons in enumerate(self.radiobuttons):
            for j, radiobutton in enumerate(radiobuttons):
                radiobutton.grid(column=2+i, row=2+j, sticky=tk.NSEW)

    def get(self, i):
        return self.variables[i].get()
    
    def set(self, i, val):
        return self.variables[i].set(val)
    
    def set_headers(self, headers):
        self.headers = headers
        self.__init_variables()
        self.__init_label_headers()
        self.__init_radiobuttons()
        self._pack()

    def __init_label_variants(self):
        self.label_variants.clear()
        for text in self.variants:
            self.label_variants.append(tk.Label(self, text=text, justify=tk.RIGHT))

    def __init_label_headers(self):
        self.label_headers.clear()
        for text in self.headers:
            self.label_headers.append(tk.Label(self, text=text, justify=tk.CENTER))

    def __init_variables(self):
        self.variables.clear()
        for component in self.headers:
            self.variables.append(tk.IntVar())
        
    def __init_radiobuttons(self):
        self.radiobuttons.clear()
        for i, header in enumerate(self.headers):
            self.radiobuttons.append([])
            for j, varian in enumerate(self.variants[:-1]):
                self.radiobuttons[i].append(tk.Radiobutton(self, variable=self.variables[i], value=j))
