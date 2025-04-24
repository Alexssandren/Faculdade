paragrafo = "Este é um exemplo de parágrafo. Este parágrafo é simples e serve para contar palavras."

palavras = paragrafo.lower().replace(".", "").split()

contagem_palavras = {}

for palavra in palavras:
    if palavra in contagem_palavras:
        contagem_palavras[palavra] += 1
    else:
        contagem_palavras[palavra] = 1

for palavra in sorted(contagem_palavras):
    print(f"{palavra}: {contagem_palavras[palavra]}")
