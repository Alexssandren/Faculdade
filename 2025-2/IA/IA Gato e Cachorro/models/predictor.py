"""
Módulo para fazer predições usando modelos treinados
"""

import os
import sys
import numpy as np
import joblib
from pathlib import Path
from PIL import Image
import cv2

# Adicionar diretório pai ao caminho para importar módulos locais
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import MODELS_DIR, CLASSES, MODEL_CONFIG, UNKNOWN_THRESHOLD, OTHER_CLASS_ID
from utils.image_utils import create_image_processor


class ImagePredictor:
    """
    Classe para fazer predições de classificação de imagens
    """

    def __init__(self, model_path=None):
        """
        Inicializa o preditor

        Args:
            model_path (str): Caminho para o modelo treinado
        """
        self.processor = create_image_processor(image_size=MODEL_CONFIG['image_size'])
        self.model = None
        self.model_info = {}
        self.pca = None

        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path):
        """
        Carrega modelo treinado

        Args:
            model_path (str): Caminho para o arquivo do modelo
        """
        try:
            model_path = Path(model_path)

            if not model_path.exists():
                # Tentar encontrar modelo mais recente automaticamente
                available_models = list(MODELS_DIR.glob('*.joblib'))
                # Excluir arquivos PCA
                available_models = [m for m in available_models if m.stem.lower() != 'pca']
                if available_models:
                    model_path = max(available_models, key=lambda p: p.stat().st_mtime)
                    print(f"[INFO] Modelo não especificado, usando mais recente: {model_path.name}")
                else:
                    raise FileNotFoundError("Nenhum modelo encontrado")

            self.model = joblib.load(model_path)

            # Carregar PCA se existir
            pca_path = model_path.parent / 'pca.joblib'
            if pca_path.exists():
                self.pca = joblib.load(pca_path)
                print("[INFO] PCA carregado")

            # Tentar carregar informações do modelo
            metrics_file = model_path.with_name(model_path.stem + '_metrics.json')
            if metrics_file.exists():
                import json
                with open(metrics_file, 'r') as f:
                    self.model_info = json.load(f)

            print(f"[OK] Modelo carregado: {model_path.name}")

        except Exception as e:
            print(f"[ERROR] Erro ao carregar modelo: {e}")
            self.model = None

    def predict_image(self, image_path):
        """
        Faz predição para uma imagem

        Args:
            image_path (str): Caminho para a imagem

        Returns:
            dict: Resultado da predição
        """
        if self.model is None:
            return {
                'error': 'Modelo não carregado',
                'prediction': None,
                'confidence': None,
                'class_name': None
            }

        try:
            # Carregar e processar imagem
            image = self.processor.load_image(image_path)
            if image is None:
                return {
                    'error': 'Erro ao carregar imagem',
                    'prediction': None,
                    'confidence': None,
                    'class_name': None
                }

            # Pré-processar imagem
            processed_image = self.processor.preprocess_image(image)
            if processed_image is None:
                return {
                    'error': 'Erro ao processar imagem',
                    'prediction': None,
                    'confidence': None,
                    'class_name': None
                }

            # Extrair features
            features = self.processor.extract_all_features(processed_image)

            # PCA
            if self.pca is not None:
                features = self.pca.transform(features.reshape(1, -1))[0]
            features = features.reshape(1, -1)  # Modelo espera 2D

            # Fazer predição
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]

            # Confidence é a probabilidade da classe predita
            confidence = probabilities[prediction]

            # Nome da classe
            class_name = CLASSES.get(prediction, 'Desconhecido')

            return {
                'prediction': int(prediction),
                'confidence': float(confidence),
                'class_name': class_name,
                'probabilities': probabilities.tolist(),
                'error': None
            }

        except Exception as e:
            return {
                'error': f'Erro na predição: {str(e)}',
                'prediction': None,
                'confidence': None,
                'class_name': None
            }

    def predict_image_from_array(self, image_array):
        """
        Faz predição usando array numpy da imagem

        Args:
            image_array (numpy.ndarray): Array da imagem

        Returns:
            dict: Resultado da predição
        """
        if self.model is None:
            return {
                'error': 'Modelo não carregado',
                'prediction': None,
                'confidence': None,
                'class_name': None
            }

        try:
            # Pré-processar imagem
            processed_image = self.processor.preprocess_image(image_array)
            if processed_image is None:
                return {
                    'error': 'Erro ao processar imagem',
                    'prediction': None,
                    'confidence': None,
                    'class_name': None
                }

            # Extrair features
            features = self.processor.extract_all_features(processed_image)
            if self.pca is not None:
                features = self.pca.transform(features.reshape(1, -1))[0]
            features = features.reshape(1, -1)

            # Fazer predição
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            confidence = probabilities[prediction]
            if confidence < UNKNOWN_THRESHOLD:
                prediction = OTHER_CLASS_ID
                class_name = CLASSES.get(OTHER_CLASS_ID, 'Outro')
            else:
                class_name = CLASSES.get(prediction, 'Desconhecido')

            return {
                'prediction': int(prediction),
                'confidence': float(confidence),
                'class_name': class_name,
                'probabilities': probabilities.tolist(),
                'error': None
            }

        except Exception as e:
            return {
                'error': f'Erro na predição: {str(e)}',
                'prediction': None,
                'confidence': None,
                'class_name': None
            }

    def get_model_info(self):
        """
        Retorna informações sobre o modelo carregado

        Returns:
            dict: Informações do modelo
        """
        return self.model_info

    def list_available_models(self):
        """
        Lista modelos disponíveis para carregamento

        Returns:
            list: Lista de caminhos dos modelos disponíveis
        """
        return list(MODELS_DIR.glob('*.joblib'))


def create_predictor(model_path=None):
    """
    Função factory para criar preditor

    Args:
        model_path (str): Caminho opcional para modelo específico

    Returns:
        ImagePredictor: Instância do preditor
    """
    return ImagePredictor(model_path)
