import pandas as pd

# Carregar o dataset
df = pd.read_excel('data/online_retail_II.xlsx', sheet_name='Year 2010-2011')

# Remover entradas com valores nulos em 'Customer ID'
df = df.dropna(subset=['Customer ID'])

# Calcular o valor total de cada transação
df['TotalPrice'] = df['Quantity'] * df['Price']

# Salvar o DataFrame preparado
df.to_pickle('data/prepared_data.pkl')
