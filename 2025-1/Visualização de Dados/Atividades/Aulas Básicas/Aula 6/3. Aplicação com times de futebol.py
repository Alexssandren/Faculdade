tabela = [
    {"time": "Flamengo", "pontos": 71},
    {"time": "Palmeiras", "pontos": 70},
    {"time": "Atlético-MG", "pontos": 65},
    {"time": "Corinthians", "pontos": 62},
    {"time": "São Paulo", "pontos": 60},
    {"time": "Internacional", "pontos": 59},
    {"time": "Grêmio", "pontos": 58},
    {"time": "Santos", "pontos": 55},
    {"time": "Fluminense", "pontos": 53},
    {"time": "Athletico-PR", "pontos": 52}
]

print("Tabela do Campeonato Brasileiro:")
for i, time in enumerate(tabela, 1):
    print(f"{i}. {time['time']}: {time['pontos']} pontos")

tabela_tuplas = [
    ("Flamengo", 71),
    ("Palmeiras", 70),
    ("Atlético-MG", 65),
]

tabela_dict = {
    "Flamengo": 71,
    "Palmeiras": 70,
    "Atlético-MG": 65,
}