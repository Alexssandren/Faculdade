conjunto1 = {1, 2, 3, 4, 5}
conjunto2 = {4, 5, 6, 7, 8}

uniao = conjunto1.union(conjunto2)
intersecao = conjunto1.intersection(conjunto2)

elemento = 3
if elemento in conjunto1:
    print(f"O elemento {elemento} está presente em conjunto 1.")
else:
    print(f"O elemento {elemento} NÃO está presente em conjunto 1.")

print("União:", uniao)
print("Interseção:", intersecao)
