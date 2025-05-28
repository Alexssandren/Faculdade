numeros = []

for i in range(1, 6):
    numeros.append(i)

numeros.remove(3)

numeros.insert(2, 6)

print(' '.join(map(str, numeros)))