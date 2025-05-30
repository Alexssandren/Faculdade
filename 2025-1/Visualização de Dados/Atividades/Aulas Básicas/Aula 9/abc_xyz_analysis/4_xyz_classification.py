import pandas as pd

# Carregar os dados preparados
df = pd.read_pickle('data/prepared_data.pkl')

# Converter a coluna 'InvoiceDate' para datetime
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# Adicionar uma coluna de mês
df['Month'] = df['InvoiceDate'].dt.to_period('M')

# Calcular a demanda mensal por produto
monthly_demand = df.groupby(['StockCode', 'Month'])['Quantity'].sum().unstack().fillna(0)

# Calcular a média e o desvio padrão da demanda
mean_demand = monthly_demand.mean(axis=1)
std_demand = monthly_demand.std(axis=1)

# Calcular o coeficiente de variação
cv = std_demand / mean_demand

# Função para classificar os produtos
def classify_xyz(coef_var):
    if coef_var <= 0.5:
        return 'X'
    elif coef_var <= 1.0:
        return 'Y'
    else:
        return 'Z'

# Aplicar a classificação
xyz_classification = cv.apply(classify_xyz)

# Salvar a classificação XYZ
xyz_classification.to_csv('data/xyz_classification.csv')
