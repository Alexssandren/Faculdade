import pandas as pd

dados = {
    "id": range(1, 11),
    "data_nascimento": [
        "2000-01-01", "1999-05-23", "2001-07-12", "1998-03-15", "2002-11-30",
        "1997-08-19", "2000-06-01", "1995-04-17", "2003-09-05", "1996-12-20"
    ],
    "CPF": [
        "11111111111", "22222222222", "33333333333", "44444444444", "55555555555",
        "66666666666", "77777777777", "88888888888", "99999999999", "00000000000"
    ],
    "nome": [
        "Ana", "Bruno", "Carlos", "Daniela", "Eduardo",
        "Fernanda", "Gabriel", "Helena", "Igor", "Joana"
    ]
}

df = pd.DataFrame(dados)

print("DataFrame Original:")
print(df)

df = df.drop(index=5)

df["cidade"] = [
    "São Paulo", "Rio de Janeiro", "Curitiba", "Belo Horizonte", "Salvador",
    "Porto Alegre", "Recife", "Fortaleza", "Manaus"
]

print("\nDataFrame Atualizado (com coluna cidade e sem a sexta linha):")
print(df)

print("\nFiltro: Pessoas nascidas após o ano 2000:")
print(df[df["data_nascimento"] > "2000-01-01"])

print("\nFiltro: Pessoas da cidade de Recife:")
print(df[df["cidade"] == "Recife"])
