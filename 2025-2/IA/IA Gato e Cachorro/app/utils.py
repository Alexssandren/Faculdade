"""
Utilitários para a aplicação Streamlit
"""

import streamlit as st
from PIL import Image
import numpy as np


def display_image_with_prediction(image, prediction):
    """
    Exibe imagem com overlay do resultado da predição

    Args:
        image (PIL.Image): Imagem original
        prediction (dict): Resultado da predição
    """
    if prediction['error']:
        st.error(f"Erro: {prediction['error']}")
        return

    # Criar duas colunas
    col1, col2 = st.columns([2, 1])

    with col1:
        st.image(image, caption="Imagem analisada", use_column_width=True)

    with col2:
        st.markdown("### Resultado")

        # Ícone e nome da classe
        icon = "[CAT]" if prediction['prediction'] == 0 else "[DOG]"
        class_name = prediction['class_name']

        st.markdown(f"**{icon} {class_name}**")

        # Confiança
        confidence = prediction['confidence']
        st.progress(confidence)
        st.markdown(f"**Confiança:** {confidence:.1%}")

        # Probabilidades
        probabilities = prediction['probabilities']
        st.markdown("#### Probabilidades:")
        st.json({
            'Gato': f"{probabilities[0]:.1%}",
            'Cachorro': f"{probabilities[1]:.1%}"
        })


def format_prediction_result(prediction):
    """
    Formata o resultado da predição para exibição

    Args:
        prediction (dict): Resultado da predição

    Returns:
        str: Texto formatado
    """
    if prediction['error']:
        return f"[ERROR] Erro: {prediction['error']}"

    icon = "[CAT]" if prediction['prediction'] == 0 else "[DOG]"
    class_name = prediction['class_name']
    confidence = prediction['confidence']

    return f"{icon} **{class_name}** (Confiança: {confidence:.1%})"


def validate_image_file(uploaded_file):
    """
    Valida arquivo de imagem carregado

    Args:
        uploaded_file: Arquivo carregado via Streamlit

    Returns:
        tuple: (is_valid, error_message)
    """
    if uploaded_file is None:
        return False, "Nenhum arquivo selecionado"

    # Verificar extensão
    valid_extensions = ['.png', '.jpg', '.jpeg']
    file_extension = Path(uploaded_file.name).suffix.lower()

    if file_extension not in valid_extensions:
        return False, f"Formato não suportado: {file_extension}"

    # Verificar tamanho (máximo 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if uploaded_file.size > max_size:
        return False, "Arquivo muito grande (máximo 10MB)"

    return True, ""


def get_image_info(image):
    """
    Obtém informações básicas sobre a imagem

    Args:
        image (PIL.Image): Imagem PIL

    Returns:
        dict: Informações da imagem
    """
    return {
        'formato': image.format,
        'tamanho': image.size,
        'modo': image.mode,
        'profundidade': len(image.getbands()) if hasattr(image, 'getbands') else 1
    }
