import csv
import random

def contar_linhas(arquivo):
    with open(arquivo, 'r', encoding='latin1') as f:
        return len(list(csv.reader(f, delimiter=';')))

def tratar_dataset(arquivo_entrada, arquivo_saida, num_linhas=1000):
    # Lê todas as linhas
    with open(arquivo_entrada, 'r', encoding='latin1') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)  # Guarda o cabeçalho
        linhas = list(reader)  # Lê todas as linhas
    
    # Se tiver mais que num_linhas, seleciona aleatoriamente
    if len(linhas) > num_linhas:
        linhas = random.sample(linhas, num_linhas)
    
    # Salva o arquivo tratado
    with open(arquivo_saida, 'w', newline='', encoding='latin1') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(header)  # Escreve o cabeçalho
        writer.writerows(linhas)  # Escreve as linhas selecionadas

def main():
    arquivo_original = 'microdados_ed_basica_2024.csv'
    arquivo_tratado = 'microdados_ed_basica_2024_tratado.csv'
    
    # Conta linhas do arquivo original
    try:
        num_linhas = contar_linhas(arquivo_original)
        print(f"\nArquivo original tem {num_linhas} linhas")
        
        if num_linhas > 1000:
            print("Tratando dataset para ter 1000 linhas...")
            tratar_dataset(arquivo_original, arquivo_tratado)
            num_linhas_novo = contar_linhas(arquivo_tratado)
            print(f"Arquivo tratado criado com {num_linhas_novo} linhas")
            print(f"Novo arquivo: {arquivo_tratado}")
        else:
            print("Arquivo já está com menos de 1000 linhas, não precisa ser tratado.")
    
    except FileNotFoundError:
        print(f"\nERRO: Arquivo {arquivo_original} não encontrado!")
    except Exception as e:
        print(f"\nERRO: {str(e)}")

if __name__ == '__main__':
    main() 