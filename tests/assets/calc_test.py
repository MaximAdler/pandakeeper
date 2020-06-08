import pandas as pd
import pandas
from pandas import read_csv, read_json
import time

print('start')
df = pd.read_csv('tests/assets/data.csv')#, skiprows=lambda x: x > 5)
print(2+2)
df = df[df['id'] > 5]
print(df[:2])