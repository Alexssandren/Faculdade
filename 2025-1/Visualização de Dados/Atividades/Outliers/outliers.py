import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

dados_normais = np.random.normal(loc=100, scale=20, size=150)

outliers = np.array([5, 10, 195, 210])

dados_completos = np.concatenate([dados_normais, outliers])

plt.figure(figsize=(10, 7))

box = plt.boxplot(dados_completos, vert=False, patch_artist=True,
                  flierprops={'markerfacecolor': 'r', 'marker': 's', 'markersize': 8})

plt.title('Visualização de Outliers com Boxplot', fontsize=16)
plt.xlabel('Valores', fontsize=12)
plt.yticks([1], ['Conjunto de Dados']) 

colors = ['lightblue']
for patch in box['boxes']:
    patch.set_facecolor(colors[0])

plt.grid(True, linestyle='--', alpha=0.6)

plt.show()