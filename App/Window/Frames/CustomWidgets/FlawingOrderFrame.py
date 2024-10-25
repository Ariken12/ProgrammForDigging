import tkinter as tk
import tkinter.ttk as ttk


R_OBJECT = 20

Y_SHIFT = 25
START_SHIFT = 100
CHAR_LENGTH = 15
WORDS_SHIFT = 10
FONT = 'Arial 15'




class FlawingOrderFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.canvas = tk.Canvas(self, height=50)
        self.labels = []
        self.objects = []
        self.x_coord = []
        self.canvas.bind('<ButtonPress-1>', self.__button_press)
        self.canvas.bind('<Motion>', self.__button_motion)
        self.canvas.bind('<ButtonRelease-1>', self.__button_release)
        self._pack()
        self.data = {
            'pressed': False,
            'component': None
            }

    def _pack(self):
        self.canvas.pack(expand=True, fill=tk.X)

    def __button_press(self, e):
        self.data['pressed'] = True
        for item in self.labels:
            item_coords = self.canvas.coords(item)
            if (item_coords[0] - e.x) ** 2 + (item_coords[1] - e.y) ** 2 < R_OBJECT ** 2:
                self.data['component'] = item
                self.canvas.coords(item, e.x, Y_SHIFT) 
                break

    def __button_motion(self, e):
        if self.data['pressed'] and self.data['component'] is not None:
            self.canvas.coords(self.data['component'], e.x, Y_SHIFT)

    def __button_release(self, e):
        self.data['pressed'] = False
        self.data['component'] = None

    def set_objects(self, objects):
        for label in self.labels:
            self.canvas.delete(label)
        self.labels.clear()
        self.objects.clear()
        self.canvas['bg'] = 'white'
        length = START_SHIFT
        for i, text in enumerate(objects):
            self.labels.append(self.canvas.create_text(length, Y_SHIFT, text=text, font=FONT))
            self.objects.append(text)
            length += CHAR_LENGTH * (len(text)) + WORDS_SHIFT
        self._pack()

    def get_order(self):
        order = []
        i = 0
        for label in self.labels:
            pos = self.canvas.coords(label)[0]
            order.append((pos, i))
            i +=1
        order.sort(key=lambda o: o[0])
        return tuple([self.objects[i[1]] for i in order])


if __name__ == '__main__':
    list = ('Fox', 'Tiger', 'Lion', 'Bird')
    root = tk.Tk()
    fof = FlawingOrderFrame(root)
    fof.set_objects(list)
    but = tk.Button(root, text='Вывести порядок', command=lambda: print(fof.get_order()))
    fof.pack(expand=True, fill=tk.BOTH)
    but.pack(expand=True, fill=tk.BOTH)
    root.mainloop()