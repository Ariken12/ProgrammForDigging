#from Window import MainWindow as mw
import Window as mw
import Core as c


def main():
    core = c.Core()
    root = mw.MainWindow()
    root.mainloop()


if __name__ == "__main__":
    main()