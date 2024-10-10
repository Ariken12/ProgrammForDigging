COLUMNS = (
    'Участок',
    'Горизонт',
    'Тип горной массы',
    'Обьем, м³',
    'Масса, т',
    'SG, т/м³'
)

COLUMNS_SIZES = (
    70,
    70,
    110,
    80,
    60,
    60
)
TABLE_HEIGHT = 5
MAX_WIDTH = 1920
FORMAT_FUNCS = {
    0: lambda x: x,
    1: lambda x: x,
    2: lambda x: x,
    3: lambda x: ' '.join([''.join(reversed(str(int(x))))[i:i+3] for i in range(0, len(str(int(x))), 3)])[::-1],
    4: lambda x: ' '.join([''.join(reversed(str(int(x))))[i:i+3] for i in range(0, len(str(int(x))), 3)])[::-1],
    5: lambda x: f'{x:.2f}',
    6: lambda x: f'{x:.3f}',
    7: lambda x: f'{x:.3f}',
    8: lambda x: f'{x:.3f}',
    9: lambda x: f'{x:.3f}',
    10: lambda x: f'{x:.3f}',
    11: lambda x: f'{x:.3f}',
    12: lambda x: f'{x:.3f}',
    13: lambda x: f'{x:.3f}',
    14: lambda x: f'{x:.3f}',
    15: lambda x: f'{x:.3f}',
    16: lambda x: f'{x:.3f}'
}