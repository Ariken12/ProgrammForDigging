import tkinter as tk
import Window.Frames as f



class MainWindow(tk.Tk):
    def __init__(self, core, *args, **kwargs):
        super().__init__()
        self.geometry('1800x1000+0+0')
        self.title('Планировщик горных работ')
        self.app_core = core
        self.parse_frame = f.ParseFile(core)
        self.data_view = f.DataView(core)
        self.menu_frame = f.MenuFrame(self)
        self.menu = tk.Menu(self)
        self.menu.add_command(label='Посмотреть данные карьера', command=self._view_resources)
        self.menu.add_command(label='Рассчитать план', command=self._start_calculation)
        self._pack()
        # -------------!!!!!!!!!!!!test command!!!!!!!!!!!------------------
        # self.parse_frame.entry_open_file.insert(0, './resources/Тест_вариант_1.xlsx')
        # self.parse_frame._load_file_command()
        # self.parse_frame._start_()
        # self.update()
        # -------------!!!!!!!!!!!!test command!!!!!!!!!!!------------------

    def _pack(self):
        # self.menu_frame.pack(expand=1, fill=tk.BOTH)
        self.parse_frame.pack(side=tk.TOP, expand=1, fill=tk.BOTH)
        # self.data_view.pack(side=tk.TOP, expand=1, fill=tk.BOTH)
        self.config(menu=self.menu)

    def _view_resources(self):
        self.parse_frame.init()
        self._switch_frames('parse_frame')

    def _start_calculation(self):
        self.data_view.init()
        self._switch_frames('data_view')

    def _switch_frames(self, mode):
        if mode == 'parse_frame':
            self.menu_frame.pack_forget()
            self.data_view.pack_forget()
            self.parse_frame.pack(expand=1, fill=tk.BOTH)
        elif mode == 'data_view':
            self.menu_frame.pack_forget()
            self.data_view.pack(expand=1, fill=tk.BOTH)
            self.parse_frame.pack_forget()
            # -------------!!!!!!!!!!!!test command!!!!!!!!!!!------------------
            # for entry in self.data_view.frame_input_parameters.entrys_acceleration + \
            #             self.data_view.frame_input_parameters.entrys_components + \
            #             self.data_view.frame_input_parameters.entrys_max_depth:
            #     entry.insert(0, '100000000')
            # self.data_view.frame_parameters_ores.variables[-1].set(1)
            # self.data_view.frame_parameters_ores.variables[-2].set(1)
            # self.data_view.frame_parameters_ores.variables[-3].set(1)
            # self.data_view.frame_parameters_ores.variables[-4].set(1)
            # self.data_view.frame_parameters_ores.variables[-5].set(1)
            # -------------!!!!!!!!!!!!test command!!!!!!!!!!!------------------
