import pandas as pd

# Criando os DataFrames de clientes e pedidos
clientes = pd.DataFrame({
    'ID': [1, 2, 3],
    'Nome': ['João', 'Maria', 'Pedro']
})

pedidos = pd.DataFrame({
    'ID do Cliente': [1, 2, 1],
    'Total do Pedido': [100, 200, 150]
})

# Realizando a junção entre os DataFrames
df_merged = pd.merge(pedidos, clientes, how='inner', left_on='ID do Cliente', right_on='ID')

df_merged
