from dateutil.relativedelta import relativedelta
import datetime as dt
d = dt.date(2020, 2, 29)
print(d)
print(d + relativedelta(years=1))