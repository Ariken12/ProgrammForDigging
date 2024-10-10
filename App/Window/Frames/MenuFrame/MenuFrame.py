import tkinter as tk
import tkinter.ttk as ttk
from Window.Frames.MenuFrame.Constants import *



class MenuFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.parent = master
        self.label_description = tk.Label(self, text=DESCR_TEXT, justify=tk.CENTER)
        self.button_input = ttk.Button(self, text=INPUT_TEXT, command=self.__goto_input)
        self.button_plan = ttk.Button(self, text=PLANNING_TEXT, command=self.__goto_dataview)
        self._pack()

    def _pack(self):
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(2, weight=1)
        self.label_description.grid(row=1, column=1, columnspan=2, sticky=tk.NSEW)
        self.button_input.grid(row=2, column=1, sticky=tk.NSEW)
        self.button_plan.grid(row=2, column=2, sticky=tk.NSEW)

    def __goto_input(self):
        self.parent._switch_to_parseframe()

    def __goto_dataview(self):
        self.parent._switch_to_dataviewframe()