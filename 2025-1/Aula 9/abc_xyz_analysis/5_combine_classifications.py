import pandas as pd

# Carregar as classificações ABC e XYZ
abc = pd.read_csv('data/abc_classification.csv', index_col=0)
xyz = pd.read_csv('data/xyz_classification.csv', index_col=0)

# Caso o CSV tenha apenas uma coluna de classificação, transforme em Series
if abc.shape[1] == 1:
    abc = abc.iloc[:, 0]
if xyz.shape[1] == 1:
    xyz = xyz.iloc[:, 0]

# Combinar as classificações
abc_xyz = pd.DataFrame({
    'ABC': abc,
    'XYZ': xyz
})

# Criar a classificação combinada
abc_xyz['ABC_XYZ'] = abc_xyz['ABC'] + abc_xyz['XYZ']

# Salvar a classificação combinada
abc_xyz.to_csv('data/abc_xyz_classification.csv')
