import tkinter as tk
import Window.Frames as f


class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.parse_frame = f.ParseFile()
        self.parse_frame.pack()