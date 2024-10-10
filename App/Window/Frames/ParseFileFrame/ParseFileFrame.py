import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import tkinter.messagebox as tkmb
import Core.Core as Core
import Core.Components as Data
import os

from Window.Frames.ParseFileFrame.Constants import *



class ParseFileFrame(tk.Frame):
    def __init__(self, core, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.core : Core = core
        self.label_name_space = tk.Label(self, text='Название месторождения*', justify=tk.CENTER)
        self.entry_name_space = tk.Entry(self, justify=tk.CENTER, font='bold')
        self.frame_third_line = tk.Frame(self)
        self.button_open_file = tk.Button(self.frame_third_line, text='Выбрать файл', command=(self._open_file_command))
        self.entry_open_file = tk.Entry(self.frame_third_line, width=120)
        self.button_load_file = tk.Button(self.frame_third_line, text='Загрузить файл', command=(self._load_file_command))
        self.button_save_file = tk.Button(self.frame_third_line, text='Сохранить файл', command=(self._save_file_command))
        self.progressbar_status = ttk.Progressbar(self, orient='horizontal', value=100)
        self.scrollbar_treeview = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.treeview_table = ttk.Treeview(self, columns=COLUMNS, displaycolumns='#all', show='headings', height=TABLE_HEIGHT,
                                           yscrollcommand=self.scrollbar_treeview.set, selectmode=tk.BROWSE)
        self.scrollbar_treeview['command'] = self.treeview_table.yview
        self.label_places = tk.Label(self, text='Информация о участках')
        self.scrollbar_places = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.text_places = tk.Text(self, yscrollcommand=self.scrollbar_places.set, width=30, height=TABLE_HEIGHT, wrap=tk.WORD, state=tk.DISABLED)
        self.scrollbar_places['command'] = self.text_places.yview
        self.label_ore_types = tk.Label(self, text='Информация о породах')
        self.scrollbar_ore_types = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.text_ore_types = tk.Text(self, yscrollcommand=self.scrollbar_ore_types.set, width=30, height=TABLE_HEIGHT, wrap=tk.WORD, state=tk.DISABLED)
        self.scrollbar_ore_types['command'] = self.text_ore_types.yview
        self.label_components = tk.Label(self, text='Информация о компонентах')
        self.scrollbar_components = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.text_components = tk.Text(self, yscrollcommand=self.scrollbar_components.set, width=30, height=TABLE_HEIGHT, wrap=tk.WORD, state=tk.DISABLED)
        self.scrollbar_components['command'] = self.text_components.yview
        self.button_load_data = tk.Button(self, text='Начать работу с данными', command=(self._start_))
        self.button_load_data['state'] = tk.DISABLED

        self._pack()
    
    def _pack(self):
        self.columnconfigure(2, weight=1)
        self.rowconfigure(6, weight=1)
        self.rowconfigure(8, weight=1)
        self.rowconfigure(10, weight=1)
        self.label_name_space.grid(         column=1, row=1,  columnspan=4, sticky=tk.NSEW)
        self.entry_name_space.grid(         column=1, row=2,  columnspan=4, sticky=tk.NSEW)
        self.button_open_file.grid(         column=1, row=1,  columnspan=1, sticky=tk.NSEW)
        self.entry_open_file.grid(          column=2, row=1,  columnspan=1, sticky=tk.NSEW)
        self.button_load_file.grid(         column=3, row=1,  columnspan=1, sticky=tk.NSEW)
        self.button_save_file.grid(         column=4, row=1,  columnspan=1, sticky=tk.NSEW)
        self.frame_third_line.grid(         column=1, row=3, columnspan=4, sticky=tk.NSEW)
        self.frame_third_line.columnconfigure(2, weight=1)
        self.progressbar_status.grid(       column=1, row=4,  columnspan=4, sticky=tk.NSEW)
        self.scrollbar_treeview.grid(       column=1, row=5,                rowspan=6, sticky=tk.NSEW)
        self.treeview_table.grid(           column=2, row=5,  columnspan=1, rowspan=6, sticky=tk.NSEW)
        self.label_places.grid(             column=3, row=5,  columnspan=1, sticky=tk.NSEW)
        self.text_places.grid(              column=3, row=6,  columnspan=1, sticky=tk.NSEW)
        self.scrollbar_places.grid(         column=4, row=6,  sticky=tk.NSEW)
        self.label_ore_types.grid(          column=3, row=7,  columnspan=1, sticky=tk.NSEW)
        self.text_ore_types.grid(           column=3, row=8,  columnspan=1, sticky=tk.NSEW)
        self.scrollbar_ore_types.grid(      column=4, row=8,  sticky=tk.NSEW)
        self.label_components.grid(         column=3, row=9,  columnspan=1, sticky=tk.NSEW)
        self.text_components.grid(          column=3, row=10, columnspan=1, sticky=tk.NSEW)
        self.scrollbar_components.grid(     column=4, row=10, sticky=tk.NSEW)
        self.button_load_data.grid(         column=1, row=12, columnspan=4, sticky=tk.NSEW)

    def init(self):
        pass
            
    def __init_treeview(self):
        columns = COLUMNS + tuple(self.core['component_types'])
        self.treeview_table['columns'] = columns
        for i in range(len(columns)):
            width = COLUMNS_SIZES[i] if i < len(COLUMNS_SIZES) else 700 // len(self.core['component_types'])
            self.treeview_table.heading(i, text=columns[i])
            self.treeview_table.column(i, width=width)
        self.treeview_table.column(1, anchor=tk.E)
        for i in range(3, 5):
            self.treeview_table.column(i, anchor=tk.E)
        for i in range(5, 6+len(self.core['component_types'])):
            self.treeview_table.column(i, anchor=tk.CENTER)
        self.treeview_table.bind('<Double-Button-1>', self.__treeview_handler)

    
    def _open_file_command(self):
        filename = fd.askopenfilename(defaultextension='.xlsx', filetypes=[('Excel documents','*.xlsx'),
                                                                           ('All files','*.*')])
        self.entry_open_file.delete(0, tk.END)
        self.entry_open_file.insert(0, filename)

    def _load_file_command(self):
        self.button_save_file['state'] = tk.DISABLED
        self.button_load_file['state'] = tk.DISABLED
        self.button_load_data['state'] = tk.DISABLED
        self.button_open_file['state'] = tk.DISABLED
        filename = self.entry_open_file.get()
        if not os.path.exists(filename):
            tkmb.showerror('Ошибка чтения файла', 'Файл не найден, укажите настоящий файл')
            return
        self.core.clean()
        parser_handler = self.core.parser(filename)
        while (status := next(parser_handler)) != 100:
            self.progressbar_status['value'] = status
            if status == -1:
                tkmb.showerror("Ошибка парсинга файла", "Ошибка: проверьте правильность формата файла")
                return
            if status == -2:
                tkmb.showwarning('Внимание', 'Разный размер горизонтов')
            self.__update_states()
            self.update()
        self.progressbar_status['value'] = 100
        self.__update_states()
        self.update()
        self.button_load_data['state'] = tk.NORMAL
        self.button_load_file['state'] = tk.NORMAL
        self.button_save_file['state'] = tk.NORMAL
        self.button_open_file['state'] = tk.NORMAL
        self.__init_treeview()
        self._fill_table()

    @staticmethod
    def fast_format(x): return ' '.join([''.join(reversed(str(int(x))))[i:i+3] for i in range(0, len(str(int(x))), 3)])[::-1]

    def __update_states(self):
        self.entry_name_space.delete(0, tk.END)
        self.entry_name_space.insert(0, self.core['namespace'])
        self.text_places['state'] = tk.NORMAL
        self.text_places.delete(0.0, tk.END)
        for place in self.core['meta']['places']:
            data = self.core['meta']['places'][place]
            self.text_places.insert(tk.END, f'{place}:\n')
            self.text_places.insert(tk.END, f'  Макс. гор.: {data["MAX_H"]}\n')
            self.text_places.insert(tk.END, f'  Мин. гор.: {data["MIN_H"]}\n')
            self.text_places.insert(tk.END, f'  Шаг гор.: {data["STEP_H"]}\n')
            self.text_places.insert(tk.END, f'  Обьем: {self.fast_format(data["V"])}\n')
            self.text_places.insert(tk.END, f'  Масса: {self.fast_format(data["M"])}\n')
            self.text_places.insert(tk.END, f'\n')
        self.text_places['state'] = tk.DISABLED
        self.text_ore_types['state'] = tk.NORMAL
        self.text_ore_types.delete(0.0, tk.END)
        for ore in self.core['meta']['ores']:
            data = self.core['meta']['ores'][ore]
            self.text_ore_types.insert(tk.END, f'{ore}:\n')
            self.text_ore_types.insert(tk.END, f'  Обьем: {self.fast_format(data["V"])}\n')
            self.text_ore_types.insert(tk.END, f'  Масса: {self.fast_format(data["M"])}\n')
            self.text_places.insert(tk.END, f'\n')
        self.text_ore_types['state'] = tk.DISABLED
        self.text_components['state'] = tk.NORMAL
        self.text_components.delete(0.0, tk.END)
        for ore in self.core['meta']['components']:
            data = self.core['meta']['components'][ore]
            self.text_components.insert(tk.END, f'{ore}:\n')
            self.text_components.insert(tk.END, f'  Масса: {self.fast_format(data)}\n')
            self.text_places.insert(tk.END, f'\n')
        self.text_components['state'] = tk.DISABLED

    def _save_file_command(self):
        filename = fd.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel documents','*.xlsx')])
        self.button_save_file['state'] = tk.DISABLED
        self.button_load_file['state'] = tk.DISABLED
        self.button_load_data['state'] = tk.DISABLED
        self.button_open_file['state'] = tk.DISABLED
        dumper_handler = self.core.dumper(filename)
        while (status := next(dumper_handler)) != 100:
            self.progressbar_status['value'] = status
            if status == -1:
                tkmb.showerror("Ошибка записи файла", "Ошибка: проверьте доступ к файлу")
                return
            self.__update_states()
            self.update()
        self.button_load_data['state'] = tk.NORMAL
        self.button_load_file['state'] = tk.NORMAL
        self.button_save_file['state'] = tk.NORMAL
        self.button_open_file['state'] = tk.NORMAL

    def _start_(self):
        self.master._start_calculation()

    def _change_precision(self, precision):
        self.precision = int(precision)
        self.precision_label.config(text=str(10 ** self.precision))

    def _clear_table(self):
        for i in self.treeview_table.get_children():
            self.treeview_table.delete(i)

    def _fill_table(self):
        self._clear_table()
        width = 6 + len(self.core['component_types'])
        for i in range(len(self.core['table'])):
            self.progressbar_status['value'] = int(i * 100 / (len(self.core['table'])))
            self.treeview_table.insert("", index=i, iid=i, values=tuple([FORMAT_FUNCS[j](self.core['table'][i][j]) for j in range(width)]))
            self.update()
        self.progressbar_status['value'] = 100
        self.update()

    def __treeview_handler(self, e):
        # check this function on windows
        treeview_index = int(self.treeview_table.focus())
        table_values = self.core['table'][treeview_index]
        self.button_save_file['state'] = tk.DISABLED
        self.button_load_file['state'] = tk.DISABLED
        self.button_load_data['state'] = tk.DISABLED
        self.button_open_file['state'] = tk.DISABLED
        add_root = tk.Tk()
        add_root.title('Ввод параметров')
        add_root.geometry('1280x75+200+200')
        headers = COLUMNS + tuple(self.core['component_types'])
        labels = []
        entrys = []
        for i, header in enumerate(headers):
            add_root.columnconfigure(i, weight=1)
            labels.append(ttk.Label(add_root, text=header))
            labels[i].grid(row=1, column=i, sticky=tk.NSEW)
            entrys.append(ttk.Entry(add_root))
            entrys[i].grid(row=2, column=i, sticky=tk.NSEW)
            entrys[i].insert(0, str(table_values[i]))

        def confirm():
            self.button_load_data['state'] = tk.NORMAL
            self.button_load_file['state'] = tk.NORMAL
            self.button_save_file['state'] = tk.NORMAL
            self.button_open_file['state'] = tk.NORMAL
            try:
                result = []
                for i, entry in enumerate(entrys):
                    if i in (0, 2):
                        result.append(entry.get())
                    else:
                        result.append(float(entry.get()))
                self.treeview_table.delete(treeview_index)
                self.treeview_table.insert('', index=treeview_index, iid=treeview_index, values=tuple([FORMAT_FUNCS[j](value) for j, value in enumerate(result)]))
                self.core['table'][treeview_index] = tuple(result)
            except: 
                tkmb.showerror('Ошибка', 'Проверьте правильность ввода')
            finally:
                add_root.destroy()
        ttk.Button(add_root, text='Подтвердить', command=confirm).grid(column=1, row=3, columnspan=len(headers), sticky=tk.NSEW)
