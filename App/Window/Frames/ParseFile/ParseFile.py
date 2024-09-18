import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import tkinter.messagebox as tkmb
import Core.Core as Core
import Core.Components as Data
import os

from Window.Frames.ParseFile.Constants import COLUMNS, COLUMNS_SIZES

TABLE_HEIGHT = 10

FORMAT_FUNCS = {
    0: lambda x: x,
    1: lambda x: x,
    2: lambda x: x,
    3: lambda x: f'{x:.0f}',
    4: lambda x: f'{x:.0f}',
    5: lambda x: f'{x:.0f}',
    6: lambda x: f'{x:.3g}',
    7: lambda x: f'{x:.3g}',
    8: lambda x: f'{x:.3g}',
    9: lambda x: f'{x:.3g}',
    10: lambda x: f'{x:.3g}',
    11: lambda x: f'{x:.3g}',
    12: lambda x: f'{x:.3g}',
    13: lambda x: f'{x:.3g}',
    14: lambda x: f'{x:.3g}',
    15: lambda x: f'{x:.3g}',
    16: lambda x: f'{x:.3g}'
}

class ParseFile(tk.Frame):
    def __init__(self, core, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.core : Core = core
        self.data : Data = self.core.data
        self.name_space_label = tk.Label(self, text='Название месторождения*', justify=tk.CENTER)
        self.name_space_entry = tk.Entry(self, justify=tk.CENTER, font='bold')
        self.open_file_button = tk.Button(self, text='Выбрать файл', command=(self._open_file_command))
        self.open_file_entry = tk.Entry(self, width=120)
        self.load_file_button = tk.Button(self, text='Загрузить файл', command=(self._load_file_command))
        self.save_file_button = tk.Button(self, text='Сохранить файл', command=(self._save_file_command))
        self.progressbar = ttk.Progressbar(self, orient='horizontal', length=100, value=100)
        self.table = ttk.Treeview(self, columns=COLUMNS, displaycolumns='#all', show='headings', height=TABLE_HEIGHT)
        self.size_of_horizont_label = tk.Label(self, text='Размер горизонта', justify=tk.CENTER)
        self.size_of_horizont_entry = tk.Entry(self, justify=tk.CENTER, state=tk.DISABLED)
        self.max_of_horizont_label = tk.Label(self, text='Максимальная высота горизонта', justify=tk.CENTER)
        self.max_of_horizont_entry = tk.Entry(self, justify=tk.CENTER, state=tk.DISABLED)
        self.ore_types_label = tk.Label(self, text='Типы пород')
        self.ore_types_text = tk.Text(self, width=10, height=TABLE_HEIGHT, wrap=tk.WORD, state=tk.DISABLED)
        self.load_data_button = tk.Button(self, text='Начать работу с данными', command=(self._start_))
        self.load_data_button['state'] = tk.DISABLED
        self._pack()
    
    def _pack(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(6, weight=1)
        self.name_space_label.grid(         column=1, row=0, columnspan=5, sticky=tk.NSEW)
        self.name_space_entry.grid(         column=1, row=1, columnspan=5, sticky=tk.NSEW)
        self.open_file_button.grid(         column=1, row=2, sticky=tk.NSEW)
        self.open_file_entry.grid(          column=2, row=2, columnspan=2, sticky=tk.NSEW)
        self.load_file_button.grid(         column=4, row=2, sticky=tk.NSEW)
        self.save_file_button.grid(         column=5, row=2, sticky=tk.NSEW)
        self.progressbar.grid(              column=1, row=3, columnspan=5, sticky=tk.NSEW)
        self.size_of_horizont_label.grid(   column=1, row=4, columnspan=2, sticky=tk.NSEW)
        self.size_of_horizont_entry.grid(   column=1, row=5, columnspan=2, sticky=tk.NSEW)
        self.max_of_horizont_label.grid(    column=3, row=4, columnspan=2, sticky=tk.NSEW)
        self.max_of_horizont_entry.grid(    column=3, row=5, columnspan=2, sticky=tk.NSEW)
        self.table.grid(                    column=1, row=6, columnspan=4, sticky=tk.NSEW)
        self.ore_types_label.grid(          column=5, row=4, rowspan=2,    sticky=tk.NSEW)
        self.ore_types_text.grid(           column=5, row=6, rowspan=1,    sticky=tk.NSEW)
        self.load_data_button.grid(         column=1, row=8, columnspan=5, sticky=tk.NSEW)
        
    def __init_treeview(self):
        columns = COLUMNS + tuple(self.data.components_types)
        self.table['columns'] = columns
        for i in range(len(columns)):
            width = COLUMNS_SIZES[i] if i < len(COLUMNS_SIZES) else 700 // len(self.data.components_types)
            self.table.heading(i, text=columns[i])
            self.table.column(i, width=width, minwidth=width)
        self.table.column(1, anchor=tk.E)
        for i in range(3, 5):
            self.table.column(i, anchor=tk.E)
        for i in range(5, 6+len(self.data.components_types)):
            self.table.column(i, anchor=tk.CENTER)

    
    def _open_file_command(self):
        filename = fd.askopenfilename(defaultextension='.xlsx', filetypes=[('All files','*.*'), 
                                                                            ('Excel documents','*.xlsx')])
        self.open_file_entry.delete(0, tk.END)
        self.open_file_entry.insert(0, filename)

    def _load_file_command(self):
        filename = self.open_file_entry.get()
        if not os.path.exists(filename):
            tkmb.showerror('Ошибка чтения файла', 'Файл не найден, укажите настоящий файл')
            return
        self.core.clean()
        parser_handler = self.core.parser(filename)
        self.data = self.core.data
        while (status := next(parser_handler)) != 100:
            self.progressbar['value'] = status
            if status == -1:
                tkmb.showerror("Ошибка парсинга файла", "Ошибка: проверьте правильность формата файла")
                return
            if status == -2:
                tkmb.showwarning('Внимание', 'Разный размер горизонтов')
            self.__update_states()
            self.update()
        self.progressbar['value'] = 100
        self.__update_states()
        self.load_data_button['state'] = tk.NORMAL
        self.update()
        self.__init_treeview()
        self._fill_table()

    def __update_states(self):
        self.name_space_entry.delete(0, tk.END)
        self.name_space_entry.insert(0, self.data.name_space)
        self.size_of_horizont_entry['state'] = tk.NORMAL
        self.size_of_horizont_entry.delete(0, tk.END)
        self.size_of_horizont_entry.insert(0, str(self.data.horizont_size))
        self.size_of_horizont_entry['state'] = tk.DISABLED
        self.max_of_horizont_entry['state'] = tk.NORMAL
        self.max_of_horizont_entry.delete(0, tk.END)
        self.max_of_horizont_entry.insert(0, str(self.data.max_horizont))
        self.max_of_horizont_entry['state'] = tk.DISABLED
        self.ore_types_text['state'] = tk.NORMAL
        self.ore_types_text.delete(0.0, tk.END)
        self.ore_types_text.insert(0.0, ' '.join(self.data.ore_types))
        self.ore_types_text['state'] = tk.DISABLED

    def _save_file_command(self):
        pass

    def _start_(self):
        self.master._start_calculation()

    def _change_precision(self, precision):
        self.precision = int(precision)
        self.precision_label.config(text=str(10 ** self.precision))

    def _clear_table(self):
        for i in self.table.get_children():
            self.table.delete(i)

    def _fill_table(self):
        self._clear_table()
        width = 6 + len(self.data.components_types)
        for i in range(len(self.data.table)):
            self.progressbar['value'] = int(i * 100 / (len(self.data.table)))
            self.table.insert("", i, values=tuple([FORMAT_FUNCS[j](self.data.table[i][j]) for j in range(width)]))
            self.update()
        self.progressbar['value'] = 100
        self.update()