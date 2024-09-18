import openpyxl as pyxl
import Core.Core as Core
class Parser:
    def __init__(self, core: Core):
        self.core = core
        self.data = self.core.data

    def __call__(self, filename):
        self.data = self.core.data
        try:
            workbook = pyxl.load_workbook(filename)
        except:
            yield -1
        worksheet = workbook[workbook.sheetnames[0]]
        self.data.table.clear()
        components = []
        for i in range(7, worksheet.max_column+1):
            cell = worksheet.cell(1, i).value
            if cell is not None:
                components.append(cell.split(',')[0])
        self.data.components_types = tuple(components)
        array = []
        last_horizont = 10 ** 9
        last_namespace = ''
        for row in range(2, worksheet.max_row+2):
            array.clear()
            self.data.table.append([])
            for column in range(1, 6+len(components)+1):
                cell = worksheet.cell(row, column).value
                if (column == 1) and (cell is None):
                    break
                if cell is None:
                    cell = 0
                array.append(cell)
                self.data.table[row-2].append(cell)
            if len(array) != 6+len(components):
                self.data.table.pop()
                continue
            nameplace = array[0]
            if nameplace not in self.data.places:
                self.data.places[nameplace] = []
            namespace = '_'.join(array[0].split('_')[:-1])
            if namespace not in self.data.name_space.split(' | '):
                if len(self.data.name_space) < 1:
                    self.data.name_space = namespace
                else:
                    self.data.name_space += ' | ' + namespace
            horizont = array[1]
            d_horizont = last_horizont - horizont
            if horizont > self.data.max_horizont:
                self.data.max_horizont = horizont
            if last_horizont == 10 ** 6:
                pass
            elif last_namespace != array[0]:
                last_horizont = 10 ** 6
            elif self.data.horizont_size == 0:
                self.data.horizont_size = d_horizont
            elif not (self.data.horizont_size == d_horizont or d_horizont == 0):
                yield -2
            last_horizont = horizont
            last_namespace = array[0]
            ore_type = array[2]
            if ore_type not in self.data.ore_types:
                self.data.ore_types.append(ore_type)
            yield int(row * 100 / (worksheet.max_row-1))
        while True:
            yield 100
        