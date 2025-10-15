notas = {}

notas["Ana"] = 8.5
notas["Bruno"] = 7.2
notas["Carla"] = 9.0

print("Nota de Bruno:", notas["Bruno"])

del notas["Ana"]

for aluno, nota in notas.items():
    print(f"{aluno}: {nota}")
