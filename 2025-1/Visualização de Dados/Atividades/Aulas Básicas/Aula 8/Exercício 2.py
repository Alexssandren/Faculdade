import pandas as pd

df = pd.DataFrame({
    "ano": [2014, 2011, 2012, 2011, 2012, 2013],
    "estado": ["PR", "SC", "RS", "RJ", "MG", "SP"],
    "desempenho": [1.5, 10.0, 3.6, 2.4, 2.9, 3.2]
}, index=["um", "dois", "três", "quatro", "cinco", "seis"])

novas_linhas = pd.DataFrame({
    "ano": [2010, 2015],
    "estado": ["BA", "CE"],
    "desempenho": [4.1, 5.3]
}, index=["sete", "oito"])

df = pd.concat([df, novas_linhas])

df = df.drop(index="cinco")

df["divida"] = [2000, 1500, 1800, 2200, 3000, 1700, 2100]

print("DataFrame atualizado:")
print(df)

print("\nFiltro: desempenho maior que 3.0")
print(df[df["desempenho"] > 3.0])

print("\nFiltro: estado igual a SP")
print(df[df["estado"] == "SP"])
