def verificar_numero(numero):
    if numero > 0:
        return "O número é positivo"
    elif numero < 0:
        return "O número é negativo" 
    else:
        return "O número é zero"

def numero_primo(numero):
    if numero <= 1:
        return False
    for i in range(2, numero):
        if numero % i == 0:
            return False
    return True

def numero_maior(numero1, numero2, numero3):
    if numero1 > numero2 and numero1 > numero3:
        return numero1
    elif numero2 > numero1 and numero2 > numero3:
        return numero2
    else:
        return numero3

def calculadora():
    print("Bem-vindo a Calculadora!")
    print("1 - Soma")
    print("2 - Subtracao") 
    print("3 - Multiplicacao")
    print("4 - Divisao")
    
    operacao = int(input("Digite o numero da operacao desejada: "))
    numero1 = float(input("Digite o primeiro numero: "))
    numero2 = float(input("Digite o segundo numero: "))
    
    if operacao == 1:
        resultado = numero1 + numero2
    elif operacao == 2:
        resultado = numero1 - numero2
    elif operacao == 3:
        resultado = numero1 * numero2
    elif operacao == 4:
        resultado = numero1 / numero2
    else:
        resultado = "Operacao invalida"
    
    if isinstance(resultado, str):
        print(resultado)
    else:
        print(f"O resultado e: {resultado}")


if __name__ == "__main__":
    calculadora()


