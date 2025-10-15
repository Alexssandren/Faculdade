"""
Script para pré-processar dados e extrair features das imagens
"""

# Adicionar diretório raiz ao sys.path antes de qualquer import local
import os, sys
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import numpy as np
import argparse
from sklearn.decomposition import PCA
import joblib
from utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, MODEL_CONFIG

print("DEBUG: RAW_DATA_DIR", RAW_DATA_DIR)

# Imports restantes
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from utils.image_utils import create_image_processor


def find_image_directories():
    """
    Encontra diretórios de imagens no dataset raw

    Returns:
        dict: Dicionário com caminhos das imagens por classe
    """
    raw_path = RAW_DATA_DIR

    # Estrutura típica do dataset cats and dogs
    # Pode ter variações dependendo do dataset específico
    image_dirs = {}

    # Procurar por diretórios comuns
    possible_dirs = ['training_set', 'test_set', 'train', 'test']

    for possible_dir in possible_dirs:
        full_path = raw_path / possible_dir
        if full_path.exists():
            print(f"📁 Encontrado diretório: {possible_dir}")

            # Dentro deste diretório, procurar cats/cats e dogs/dogs
            cats_dir = full_path / 'cats'
            dogs_dir = full_path / 'dogs'

            if cats_dir.exists() and dogs_dir.exists():
                image_dirs['cats'] = cats_dir
                image_dirs['dogs'] = dogs_dir
                print(f"  🐱 Gatos: {cats_dir}")
                print(f"  🐶 Cachorros: {dogs_dir}")
                return image_dirs

    # Se não encontrou estrutura padrão, listar todos os diretórios
    print("🔍 Procurando estrutura alternativa...")
    subdirs = [d for d in raw_path.rglob('*') if d.is_dir()]

    for subdir in subdirs:
        dir_name = subdir.name.lower()
        if 'cat' in dir_name:
            image_dirs['cats'] = subdir
            print(f"  🐱 Gatos: {subdir}")
        elif 'dog' in dir_name:
            image_dirs['dogs'] = subdir
            print(f"  🐶 Cachorros: {subdir}")

    if not image_dirs:
        print("❌ Não foi possível encontrar diretórios de gatos e cachorros")
        print("📋 Estrutura encontrada:")
        for subdir in subdirs[:10]:  # Mostrar primeiras 10
            print(f"  - {subdir}")
        if len(subdirs) > 10:
            print(f"  ... e mais {len(subdirs) - 10} diretórios")

    return image_dirs


def collect_image_paths(image_dirs):
    """
    Coleta caminhos de todas as imagens

    Args:
        image_dirs (dict): Dicionário com caminhos das imagens por classe

    Returns:
        list: Lista de tuplas (caminho_imagem, label)
    """
    image_paths = []

    for class_name, dir_path in image_dirs.items():
        if not dir_path.exists():
            print(f"⚠️  Diretório {class_name} não existe: {dir_path}")
            continue

        # Procurar arquivos de imagem
        image_extensions = ['*.jpg', '*.jpeg', '*.png']

        for ext in image_extensions:
            found_images = list(dir_path.rglob(ext))
            for img_path in found_images:
                label = 0 if class_name == 'cats' else 1  # 0 = gato, 1 = cachorro
                image_paths.append((str(img_path), label))

    print(f"📊 Total de imagens encontradas: {len(image_paths)}")
    return image_paths


def extract_features_batch(image_paths, processor, batch_size=100):
    """
    Extrai features em lotes para melhor performance

    Args:
        image_paths (list): Lista de caminhos das imagens
        processor (ImageProcessor): Processador de imagens
        batch_size (int): Tamanho do lote

    Returns:
        tuple: (features, labels)
    """
    all_features = []
    all_labels = []

    total_images = len(image_paths)
    print(f"🔄 Extraindo features de {total_images} imagens em lotes de {batch_size}")

    from tqdm.auto import tqdm

    for i in tqdm(range(0, total_images, batch_size), desc="🔄 Extraindo", unit="batch"):
        batch_paths = image_paths[i:i + batch_size]
        batch_features = []
        batch_labels = []

        for img_path, label in batch_paths:
            # Carregar e processar imagem
            image = processor.load_image(img_path)
            processed_image = processor.preprocess_image(image)

            if processed_image is not None:
                # Extrair features
                features = processor.extract_all_features(processed_image)
                batch_features.append(features)
                batch_labels.append(label)

        if batch_features:
            all_features.extend(batch_features)
            all_labels.extend(batch_labels)

            pass  # tqdm já mostra progresso

    return np.array(all_features), np.array(all_labels)


def save_processed_data(features, labels, output_dir):
    """
    Salva dados processados

    Args:
        features (numpy.ndarray): Features extraídas
        labels (numpy.ndarray): Labels das imagens
        output_dir (Path): Diretório de saída
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Salvar arrays
    np.save(output_dir / 'features.npy', features)
    np.save(output_dir / 'labels.npy', labels)

    # Salvar informações sobre o dataset
    dataset_info = {
        'n_samples': int(len(features)),
        'n_features': int(features.shape[1]) if len(features.shape) > 1 else 0,
        'n_cats': int(np.sum(labels == 0)),
        'n_dogs': int(np.sum(labels == 1)),
        'image_size': MODEL_CONFIG['image_size'],
        'feature_types': ['color', 'texture', 'shape']
    }

    # Salvar como JSON
    import json
    with open(output_dir / 'dataset_info.json', 'w') as f:
        json.dump(dataset_info, f, indent=2)

    print(f"💾 Dados salvos em: {output_dir}")
    print(f"📊 {dataset_info['n_samples']} amostras processadas")
    print(f"🎨 {dataset_info['n_cats']} gatos, {dataset_info['n_dogs']} cachorros")


def main():
    """
    Função principal para pré-processamento dos dados
    """
    # Argumentos de linha de comando
    parser = argparse.ArgumentParser(description="Pré-processamento e extração de features")
    parser.add_argument("--sample_fraction", type=float, default=1.0,
                        help="Fração do dataset a ser utilizada (0 < f ≤ 1). Ex.: 0.2 para 20% das imagens")
    args = parser.parse_args()

    if not (0 < args.sample_fraction <= 1):
        print("❌ --sample_fraction deve estar entre 0 e 1")
        sys.exit(1)

    print("🚀 Iniciando pré-processamento de dados...")

    # Passo 1: Encontrar diretórios de imagens
    print("\n📁 Passo 1: Encontrando diretórios de imagens")
    image_dirs = find_image_directories()

    if not image_dirs:
        print("❌ Não foi possível encontrar dados de treinamento")
        return

    # Passo 2: Coletar caminhos das imagens
    print("\n🔍 Passo 2: Coletando caminhos das imagens")
    image_paths = collect_image_paths(image_dirs)

    # Amostragem aleatória se necessário
    if args.sample_fraction < 1.0:
        np.random.seed(MODEL_CONFIG['random_state'])
        np.random.shuffle(image_paths)
        sample_size = int(len(image_paths) * args.sample_fraction)
        image_paths = image_paths[:sample_size]
        print(f"📉 Amostragem ativada: usando {sample_size} de {len(image_paths)} imagens")

    if not image_paths:
        print("❌ Nenhuma imagem encontrada")
        return

    # Passo 3: Criar processador de imagens
    print("\n⚙️  Passo 3: Configurando processador de imagens")
    processor = create_image_processor(image_size=MODEL_CONFIG['image_size'])
    print(f"📏 Tamanho das imagens: {MODEL_CONFIG['image_size']}")

    # Passo 4: Extrair features
    print("\n🔬 Passo 4: Extraindo features")
    features, labels = extract_features_batch(image_paths, processor)
    # Reduzir uso de memória
    features = features.astype(np.float32)

    # Aplicar PCA para redução de dimensionalidade
    print("\n📉 Aplicando PCA (300 componentes)...")
    n_components = min(300, features.shape[1])
    pca = PCA(n_components=n_components, random_state=MODEL_CONFIG['random_state'])
    features_reduced = pca.fit_transform(features)
    print(f"🔽 Dimensão original: {features.shape[1]} -> reduzida: {features_reduced.shape[1]}")

    # Salvar PCA para uso na inferência
    MODELS_DIR.mkdir(exist_ok=True, parents=True)
    joblib.dump(pca, MODELS_DIR / 'pca.joblib')

    features = features_reduced  # substituir

    if len(features) == 0:
        print("❌ Nenhuma feature extraída")
        return

    # Passo 5: Salvar dados processados
    print("\n💾 Passo 5: Salvando dados processados")
    save_processed_data(features, labels, PROCESSED_DATA_DIR)

    # Passo 6: Dividir em treino e teste
    print("\n✂️  Passo 6: Dividindo dados em treino e teste")
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels,
        test_size=MODEL_CONFIG['test_size'],
        random_state=MODEL_CONFIG['random_state'],
        stratify=labels
    )

    # Salvar conjuntos de treino e teste
    train_dir = PROCESSED_DATA_DIR / 'train'
    test_dir = PROCESSED_DATA_DIR / 'test'

    train_dir.mkdir(exist_ok=True)
    test_dir.mkdir(exist_ok=True)

    np.save(train_dir / 'X_train.npy', X_train)
    np.save(train_dir / 'y_train.npy', y_train)
    np.save(test_dir / 'X_test.npy', X_test)
    np.save(test_dir / 'y_test.npy', y_test)

    print("✅ Dados divididos em treino e teste")
    print(f"📊 Treino: {len(X_train)} amostras")
    print(f"📊 Teste: {len(X_test)} amostras")

    print("\n🎉 Pré-processamento concluído com sucesso!")


if __name__ == "__main__":
    main()
