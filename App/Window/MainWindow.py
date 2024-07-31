import tkinter as tk
import Window.Frames as f

name = 'Участок'
data = 'Вскрыша_1 Вскрыша_2 Вскрыша_3 Вскрыша_4 Вскрыша_5 Руда_сорт_1 Руда_сорт_2 Руда_сорт_3 Руда_сорт_4 Руда_сорт_5'


class MainWindow(tk.Tk):
    def __init__(self, core, *args, **kwargs):
        super().__init__()
        self.app_core = core
        self.parse_frame = f.ParseFile(core)
        self.data_view = f.DataView(core)
        self.parse_frame.columnconfigure(1, weight=1)
        self.parse_frame.rowconfigure(1, weight=1)
        # self.data_view.init()
        # self.data_view.pack(expand=1, fill=tk.BOTH)
        self.parse_frame.pack(expand=1, fill=tk.BOTH)
        self.parse_frame.open_file_entry.insert(0, './resources/input1.xlsx')
        self.parse_frame._load_file_command()
        self.parse_frame._start_()
        self.update()

    def _start_calculation(self):
        self.data_view.init()
        self._switch_frames('data_view')

    def _switch_frames(self, mode):
        if mode == 'parse_frame':
            self.data_view.pack_forget()
            self.parse_frame.pack(expand=1, fill=tk.BOTH)
        elif mode == 'data_view':
            self.data_view.pack(expand=1, fill=tk.BOTH)
            self.parse_frame.pack_forget()