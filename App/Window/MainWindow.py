import tkinter as tk
import Window.Frames as f

name = 'Участок'
data = 'Вскрыша_1 Вскрыша_2 Вскрыша_3 Вскрыша_4 Вскрыша_5 Руда_сорт_1 Руда_сорт_2 Руда_сорт_3 Руда_сорт_4 Руда_сорт_5'

class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.parse_frame = f.ParseFile()
        self.data_view = f.DataView()
        #self.data_view.columnconfigure(1, weight=1)
        #self.data_view.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.data_view.grid(column=1, row=1, sticky=tk.NSEW)
        self.data_view.init(name, data.split())