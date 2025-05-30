frase = "Programar é transformar café em código."

frase = frase.lower()

letras = set()

for caractere in frase:
    if caractere.isalpha():
        letras.add(caractere)

for letra in sorted(letras):
    print(letra)
