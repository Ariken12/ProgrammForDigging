import openpyxl as pyxl
import Core.Core as Core

MAX_H = 10 ** 9

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
        self.data.clear()
        components = []
        for i in range(7, worksheet.max_column+1):
            cell = worksheet.cell(1, i).value
            if cell is not None:
                if ',' in cell:
                    components.append(cell.split(',')[0])
                else:
                    components(str(cell))
        self.data.components_types = tuple(components)
        array = []
        self.last_horizont = MAX_H
        self.last_namespace = ''
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
            if None in array:
                continue
            if (err := self.check_nameplace(array[0]) is not None):
                yield err
            if (err := self.check_horizont(array[1]) is not None):
                yield err
            if (err := self.check_ore(array[2]) is not None):
                yield err
            for i, component in enumerate(self.data.components_types):
                if (err := self.check_components(component, array[6+i]) is not None):
                    yield err

            yield int(row * 100 / (worksheet.max_row-1))
        while True:
            yield 100
        

    def check_nameplace(self, nameplace):
        self.namespace = nameplace
        if self.namespace not in self.data.name_space.split(' | '):
            if len(self.data.name_space) < 1:
                self.data.name_space = self.namespace
            else:
                self.data.name_space += ' | ' + self.namespace
        if nameplace not in self.data.places:
            self.data.places.append(nameplace)
            self.data.meta['places'][nameplace] = {
                'V': 0, 
                'M': 0,
                'MIN_H': MAX_H,
                'MAX_H': -1,
                'STEP_H': -1
            }
        self.data.meta['places'][nameplace]['V'] += self.data.table[-1][3]
        self.data.meta['places'][nameplace]['M'] += self.data.table[-1][4]

    def check_horizont(self, horizont):
        self.data.meta['places'][self.namespace]['MIN_H'] = min(self.data.meta['places'][self.namespace]['MIN_H'], horizont)
        self.data.meta['places'][self.namespace]['MAX_H'] = max(self.data.meta['places'][self.namespace]['MAX_H'], horizont)
        d_horizont = self.last_horizont - horizont
        if self.last_namespace != self.namespace or d_horizont == MAX_H - horizont:
            self.last_horizont = horizont
            self.last_namespace = self.namespace
            return None
        self.last_horizont = horizont
        self.last_namespace = self.namespace
        if self.data.meta['places'][self.namespace]['STEP_H'] == -1 and d_horizont != 0:
            self.data.meta['places'][self.namespace]['STEP_H'] = d_horizont
        elif not (self.data.meta['places'][self.namespace]['STEP_H'] == d_horizont or d_horizont == 0):
            return -2

    def check_ore(self, ore):
        if ore not in self.data.ore_types:
            self.data.ore_types.append(ore)
            self.data.meta['ores'][ore] = {'V': 0, 'M': 0}
        self.data.meta['ores'][ore]['V'] += self.data.table[-1][3]
        self.data.meta['ores'][ore]['M'] += self.data.table[-1][4]

    def check_components(self, component, sg):
        if component not in self.data.meta['components']:
            self.data.meta['components'][component] = 0
        self.data.meta['components'][component] += self.data.table[-1][4] * sg 
        