import pandas as pd

alunos = pd.DataFrame({
    "Nome": ["Ana", "Bruno", "Carla", "Daniel", "Eduarda", "Fábio", "Giulia", "Henrique"],
    "Idade": [12, 14, 17, 19, 15, 21, 23, 18],
    "Nota": [8.5, 7.0, 9.2, 6.8, 7.5, 8.0, 9.0, 6.5]
})

bins = [10, 15, 20, 25]
labels = ["10-15 anos", "16-20 anos", "21-25 anos"]

alunos["Faixa Etária"] = pd.cut(alunos["Idade"], bins=bins, labels=labels, right=True)

media_notas = alunos.groupby("Faixa Etária")["Nota"].mean().reset_index()

print("Média das notas por faixa etária:")
print(media_notas)
