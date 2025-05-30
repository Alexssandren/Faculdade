import pandas as pd

# Carregar os dados preparados
df = pd.read_pickle('data/prepared_data.pkl')

# Calcular a receita total por produto
product_revenue = df.groupby('StockCode')['TotalPrice'].sum().sort_values(ascending=False)

# Calcular a porcentagem acumulada da receita
cumulative_percentage = product_revenue.cumsum() / product_revenue.sum() * 100

# Função para classificar os produtos
def classify_abc(percentage):
    if percentage <= 80:
        return 'A'
    elif percentage <= 95:
        return 'B'
    else:
        return 'C'

# Aplicar a classificação
abc_classification = cumulative_percentage.apply(classify_abc)

# Salvar a classificação ABC
abc_classification.to_csv('data/abc_classification.csv')
