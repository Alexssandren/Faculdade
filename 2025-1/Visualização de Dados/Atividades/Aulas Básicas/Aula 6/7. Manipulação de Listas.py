frutas = ['maçã', 'laranja', 'abacaxi', 'pera', 'manga']

frutas.sort(reverse=True)

frutas.pop(1)

frutas.append('uva')
frutas.insert(0, 'banana')

if 'morango' in frutas:
    print("Morango está na lista de frutas")
else:
    print("Morango não está na lista de frutas")