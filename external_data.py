import datetime

date = '02.03.2023'
date_o = datetime.datetime.strptime(date, "%d.%m.%Y")
print(type(date_o))

now = datetime.datetime.now()

if date_o > now:
    print(True)
else:
    print(False)