import os
import pandas as pd


def save(result, x):
    filename = 'RacingPost111 #%s.xls' % x
    writer = pd.ExcelWriter(filename)
    result.to_excel(writer)
    writer.save()


files = []
path = '.'
filenames = os.listdir(path)
for filename in filenames:
    if filename.endswith('.xls'):
        fil = pd.read_excel(filename)
        files.append(fil)

a = 0
for x in range(1, len(files)):
    print(x)
    if x % 11 == 0:
        print(a, x)
        result = pd.concat(files[a:x], ignore_index=True)
        save(result, x)
        a += 11
    elif x == len(files) - 1:
        print('vse')
        print(a, x)
        result = pd.concat(files[a:x], ignore_index=True)
        save(result, x)

