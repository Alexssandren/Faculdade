"""
Utilitários para processamento e manipulação de imagens
"""

import cv2
import numpy as np
from PIL import Image
import os
from pathlib import Path
from .config import MODEL_CONFIG, RAW_DATA_DIR, PROCESSED_DATA_DIR
from models.feature_extractor import extract_features as fe_extract


class ImageProcessor:
    """Classe para processar e extrair features de imagens"""

    def __init__(self, image_size=(64, 64)):
        """
        Inicializa o processador de imagens

        Args:
            image_size (tuple): Tamanho para resize (largura, altura)
        """
        self.image_size = image_size

    def load_image(self, image_path):
        """
        Carrega uma imagem de arquivo

        Args:
            image_path (str): Caminho para a imagem

        Returns:
            numpy.ndarray: Imagem carregada
        """
        try:
            # Usar PIL para carregar a imagem
            image = Image.open(image_path)
            return np.array(image)
        except Exception as e:
            print(f"Erro ao carregar imagem {image_path}: {e}")
            return None

    def preprocess_image(self, image):
        """
        Pré-processa uma imagem para extração de features

        Args:
            image (numpy.ndarray): Imagem de entrada

        Returns:
            numpy.ndarray: Imagem pré-processada
        """
        if image is None:
            return None

        # Resize da imagem
        image = cv2.resize(image, self.image_size)

        # Se a imagem tiver canal alpha, remover
        if image.shape[-1] == 4:
            image = image[:, :, :3]

        # Normalizar pixels para [0, 1]
        image = image.astype(np.float32) / 255.0

        return image

    def extract_color_features(self, image):
        """
        Extrai features baseadas em cores da imagem

        Args:
            image (numpy.ndarray): Imagem de entrada

        Returns:
            numpy.ndarray: Features de cor
        """
        if image is None:
            return np.zeros(9)  # 3 canais RGB * 3 estatísticas cada

        features = []

        # Para cada canal de cor (R, G, B)
        for channel in range(3):
            channel_data = image[:, :, channel]

            # Estatísticas básicas
            mean_val = np.mean(channel_data)
            std_val = np.std(channel_data)
            median_val = np.median(channel_data)

            features.extend([mean_val, std_val, median_val])

        return np.array(features)

    def extract_texture_features(self, image):
        """
        Extrai features de textura usando análise de bordas

        Args:
            image (numpy.ndarray): Imagem de entrada

        Returns:
            numpy.ndarray: Features de textura
        """
        if image is None:
            return np.zeros(4)

        # Converter para escala de cinza
        gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)

        # Detectar bordas usando Canny
        edges = cv2.Canny(gray, 100, 200)

        # Calcular estatísticas das bordas
        edge_density = np.sum(edges > 0) / edges.size

        # Calcular variância da textura
        texture_variance = np.var(gray.astype(np.float32))

        # Calcular contraste
        contrast = gray.max() - gray.min()

        # Calcular energia (soma dos quadrados)
        energy = np.sum(gray.astype(np.float32) ** 2) / gray.size

        return np.array([edge_density, texture_variance, contrast, energy])

    def extract_shape_features(self, image):
        """
        Extrai features básicas de forma

        Args:
            image (numpy.ndarray): Imagem de entrada

        Returns:
            numpy.ndarray: Features de forma
        """
        if image is None:
            return np.zeros(3)

        # Converter para escala de cinza
        gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)

        # Calcular momentos de Hu (7 momentos)
        moments = cv2.moments(gray)
        hu_moments = cv2.HuMoments(moments)

        # Usar apenas os 3 primeiros momentos (mais significativos)
        shape_features = hu_moments[:3].flatten()

        # Adicionar aspect ratio (relação largura/altura)
        height, width = gray.shape
        aspect_ratio = width / height if height > 0 else 0

        return np.array([*shape_features, aspect_ratio])

    def extract_all_features(self, image):
        """Wrapper que usa o extrator avançado de features."""
        return fe_extract(image)

    def process_dataset(self, dataset_path, output_path=None):
        """
        Processa um dataset completo e extrai features

        Args:
            dataset_path (str): Caminho para o diretório do dataset
            output_path (str): Caminho para salvar features processadas

        Returns:
            tuple: (features, labels)
        """
        features = []
        labels = []

        dataset_path = Path(dataset_path)

        # Classes (gato = 0, cachorro = 1)
        classes = {'cat': 0, 'dog': 1}

        for class_name, label in classes.items():
            class_dir = dataset_path / class_name

            if not class_dir.exists():
                print(f"Diretório {class_dir} não encontrado. Pulando...")
                continue

            print(f"Processando classe: {class_name}")

            for image_file in class_dir.glob('*'):
                if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    # Carregar imagem
                    image = self.load_image(str(image_file))

                    # Pré-processar
                    processed_image = self.preprocess_image(image)

                    if processed_image is not None:
                        # Extrair features
                        image_features = self.extract_all_features(processed_image)

                        features.append(image_features)
                        labels.append(label)

        features = np.array(features)
        labels = np.array(labels)

        if output_path:
            output_path = Path(output_path)
            output_path.mkdir(parents=True, exist_ok=True)

            # Salvar features e labels
            np.save(output_path / 'features.npy', features)
            np.save(output_path / 'labels.npy', labels)

            print(f"Features salvas em: {output_path}")

        return features, labels


def create_image_processor(image_size=(64, 64)):
    """
    Função factory para criar processador de imagens

    Args:
        image_size (tuple): Tamanho para resize

    Returns:
        ImageProcessor: Instância do processador
    """
    return ImageProcessor(image_size)
