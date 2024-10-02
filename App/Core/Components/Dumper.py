import openpyxl as pyxl
import Core.Core as Core

HEADERS = (
    'Участок',
    'Горизонт',
    'Тип горной массы',
    'Обьем, м³',
    'Масса, т',
    'SG, т/м³'
)

class Dumper:
    def __init__(self, core: Core):
        self.core = core

    def __call__(self, filename):
        self.data = self.core.data
        workbook = pyxl.Workbook()
        workbook.remove(workbook.active)
        workbook.create_sheet('Данные о карьере')
        ws = workbook['Данные о карьере']
        for col in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            ws.column_dimensions[col].width = 15
        ws.append(HEADERS + tuple(self.data.components_types))
        for i, row in enumerate(self.data.table):
            ws.append(row)
            yield i * 100 / len(self.data.table)
        try:
            workbook.save(filename)
        except Exception as e:
            yield -1
        while True:
            yield 100