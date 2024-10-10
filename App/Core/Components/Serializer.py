import pickle
import copy

class Serializer:
    def __init__(self, core):
        self.core = core

    def __call__(self, mode, name):
        self.data = self.core.data
        self.filename = name
        if mode == 'SAVE':
            self.__save()
        elif mode == 'LOAD':
            self.__load()

    def __save(self):
        with open(self.filename, 'wb') as file:
            pickle.dump(self.core, file, 5)

    def __load(self):
        with open(self.filename, 'rb') as file:
            temp = pickle.load(file)
            self.core.clean()
            for param in tuple(temp.__dict__):
                self.core.__dict__[param] = copy.deepcopy(temp.__dict__[param])
            del temp