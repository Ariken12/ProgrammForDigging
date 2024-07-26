import os
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox as tkmb
from win32com.shell import shell, shellcon
from win32com.client import Dispatch
import json

with open('users.json', 'r') as file:
    USERS = json.load(file)
MODES = ['notify', 'window']

class Installer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Установщик")
        #self.root.geometry("500x500+100+100")

        self.startup_path = shell.SHGetKnownFolderPath(shellcon.FOLDERID_Startup)
        self.shortcut_filename = self.startup_path + '\\AtlassianNotify.lnk'
        self.appsfolder_path = 'C:\\Program Files (x86)'
        self.notifier_path = self.appsfolder_path + '\\AtlassianNotify'

        self.user = tk.StringVar()
        self.mode = tk.StringVar()
        self.status_user = ttk.Combobox(self.root, textvariable=self.user, values=USERS, font='Arial 20')
        self.status_type = ttk.Combobox(self.root, textvariable=self.mode, values=MODES, font='Arial 20')
        self.status_folder = tk.Label(self.root, text=f'{self.notifier_path}', font='Arial 20')
        self.status_procceed = tk.Label(self.root, text=f'Ожидание', font='Arial 20')
        self.button_run = tk.Button(self.root, text='Запуск', command=self.start_install, font='Arial 20')
        self.status_user.pack(expand=True, fill=tk.X)
        self.status_type.pack(expand=True, fill=tk.X)
        self.status_folder.pack(expand=True, fill=tk.X)
        self.status_procceed.pack(expand=True, fill=tk.BOTH)
        self.button_run.pack(expand=True, fill=tk.BOTH)
        self.mode.set(MODES[1])
        self.root.mainloop()


    def start_install(self):
        self.status_user.config(state='disabled')
        self.status_type.config(state='disabled')
        self.status_procceed.config(text='Завершение старой программы')
        err = os.system('taskkill /f /T /Im script.exe')
        if err != 0:
            self.status_procceed.config(text='Программа не найдена')
        self.status_procceed.config(text='Составление конфигурации')
        with open('config.json', 'w') as file:
            config = {
                'user': self.user.get(),
                'mode': self.mode.get()
            }
            json.dump(config, file)
        self.status_procceed.config(text='Создание папки приложения')
        err = os.system(f'mkdir "{self.notifier_path}"')
        if err != 0:
            self.status_procceed.config(text='Ошибка создания папки, возможно она уже создана...')
        err = os.system(f'copy script.exe "{self.notifier_path}\\script.exe"')
        if err != 0:
            self.status_procceed.config(text='Ошибка копирования скрипта, проверьте права администратора')
            
        err = os.system(f'copy config.json "{self.notifier_path}\\config.json"')
        if err != 0:
            self.status_procceed.config(text='Ошибка копирования конфигурации, проверьте права администратора')
        self.status_procceed.config(text='Создание ярлыка')
        self.create_shortcut()
        self.status_procceed.config(text='Готово')

    def create_shortcut(self):
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(self.shortcut_filename)
        shortcut.TargetPath = self.notifier_path + '\\script.exe'
        shortcut.Arguments = ''
        shortcut.WorkingDirectory = self.notifier_path
        shortcut.save() 

if __name__ == "__main__":
    Installer()