import pandas as pd

path = r'C:/Users/26592/Desktop/大数据课设/'
filename = r'output'

df = pd.read_csv(f'{path}{filename}.csv')
df_cleaned = df.dropna()
df_cleaned.to_csv(f'{path}{filename}_cleaned.csv', index=False)
