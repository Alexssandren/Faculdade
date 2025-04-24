import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Carregar a classificação combinada
abc_xyz = pd.read_csv('data/abc_xyz_classification.csv', index_col=0)

# Contar a quantidade de produtos em cada classe
class_counts = abc_xyz['ABC_XYZ'].value_counts().sort_index()

# Plotar a distribuição das classes
plt.figure(figsize=(10, 6))
sns.barplot(x=class_counts.index, y=class_counts.values, palette='viridis')
plt.title('Distribuição das Classes ABC-XYZ')
plt.xlabel('Classe ABC-XYZ')
plt.ylabel('Número de Produtos')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('data/abc_xyz_distribution.png')
plt.show()
