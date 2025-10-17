"""
Aplicação principal Streamlit para classificação de imagens
"""

import os
import sys
import streamlit as st
import numpy as np
from PIL import Image
import io
from pathlib import Path

# Adicionar diretório pai ao caminho para importar módulos locais
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from utils.config import STREAMLIT_CONFIG, CLASSES, MODELS_DIR
from models.predictor import create_predictor


def main():
    """Função principal da aplicação"""

    # Configuração da página
    st.set_page_config(
        page_title=STREAMLIT_CONFIG['page_title'],
        page_icon=STREAMLIT_CONFIG['page_icon'],
        layout=STREAMLIT_CONFIG['layout'],
        initial_sidebar_state=STREAMLIT_CONFIG['initial_sidebar_state']
    )

    # Título principal
    st.title("Classificador de Gatos e Cachorros")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("Sobre")
        st.markdown("""
        Esta aplicação usa Machine Learning para classificar imagens entre **gatos** e **cachorros**.

        **Como funciona:**
        - Faça upload de uma imagem
        - O modelo extrai características visuais
        - Classifica como gato ou cachorro
        - Mostra o resultado com confiança
        """)

        st.markdown("---")

        # Seleção de modelo
        st.subheader("Modelo")
        available_models = list(MODELS_DIR.glob('*.joblib'))
        # Excluir arquivo PCA
        available_models = [m for m in available_models if m.stem.lower() != 'pca']

        if available_models:
            model_names = [m.stem for m in available_models]
            selected_model = st.selectbox(
                "Escolha o modelo:",
                model_names,
                index=0 if model_names else None
            )
            model_path = MODELS_DIR / f"{selected_model}.joblib"
        else:
            st.warning("Nenhum modelo treinado encontrado!")
            st.info("Execute o treinamento primeiro: `python training/train_model.py`")
            model_path = None

        st.markdown("---")
        st.markdown("**Desenvolvido com:**")
        st.markdown("- Python")
        st.markdown("- Scikit-learn")
        st.markdown("- OpenCV")
        st.markdown("- Streamlit")

    # Área principal
    if model_path and model_path.exists():
        # Inicializar preditor
        if 'predictor' not in st.session_state:
            with st.spinner("Carregando modelo..."):
                st.session_state.predictor = create_predictor(str(model_path))

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Upload da Imagem")

            # Upload de arquivo
            uploaded_file = st.file_uploader(
                "Escolha uma imagem de gato ou cachorro",
                type=['png', 'jpg', 'jpeg'],
                help="Formatos suportados: PNG, JPG, JPEG"
            )

            if uploaded_file is not None:
                # Mostrar imagem carregada
                image = Image.open(uploaded_file)

                # Redimensionar se necessário
                if image.size[0] > 400 or image.size[1] > 400:
                    image.thumbnail((400, 400), Image.Resampling.LANCZOS)
                    # use_container_width evita deprecation
                st.image(image, caption="Imagem carregada", use_container_width=True)

                # Botão de classificação
                if st.button("Classificar Imagem", type="primary"):
                    classify_image(image, st.session_state.predictor)

        with col2:
            st.subheader("Resultados")

            # Placeholder para resultados
            if 'last_prediction' in st.session_state:
                show_prediction_results(st.session_state.last_prediction)
            else:
                st.info("Faca upload de uma imagem e clique em 'Classificar'")

    else:
        st.error("Modelo não encontrado!")
        st.info("Certifique-se de que executou o treinamento do modelo.")

        # Mostrar instruções
        st.subheader("Como começar:")
        st.markdown("""
        1. **Baixe os dados:**
           ```bash
           cd training
           python download_data.py
           ```

        2. **Pré-processe as imagens:**
           ```bash
           python preprocess_data.py
           ```

        3. **Treine o modelo:**
           ```bash
           python train_model.py
           ```

        4. **Execute a aplicação:**
           ```bash
           cd app
           streamlit run main.py
           ```
        """)

    # Rodapé
    st.markdown("---")
    st.markdown("*Aplicação desenvolvida para classificação de imagens usando Machine Learning*")


def classify_image(image, predictor):
    """
    Classifica uma imagem usando o preditor

    Args:
        image (PIL.Image): Imagem a ser classificada
        predictor (ImagePredictor): Preditor carregado
    """
    with st.spinner("Analisando imagem..."):
        # Converter PIL Image para numpy array
        image_array = np.array(image)

        # Fazer predição
        result = predictor.predict_image_from_array(image_array)

        # Armazenar resultado na sessão
        st.session_state.last_prediction = result

        if result['error']:
            st.error(f"Erro na classificação: {result['error']}")
        else:
            st.success("Classificação concluída!")


def show_prediction_results(prediction):
    """
    Mostra os resultados da predição

    Args:
        prediction (dict): Resultado da predição
    """
    # Resultado principal
    class_name = prediction['class_name']
    confidence = prediction['confidence']

    # Se classe desconhecida
    if prediction['prediction'] == -1:
        st.warning("Classe desconhecida ou baixa confiança.")

    # Ícone baseado na classe
    if prediction['prediction'] == 0:
        icon = '[CAT]'
    elif prediction['prediction'] == 1:
        icon = '[DOG]'
    else:
        icon = '[OTHER]'

    st.markdown(f"### {icon} Resultado: **{class_name}**")

    # Barra de progresso para confiança
    if confidence is not None:
        st.progress(confidence)
    else:
        st.warning("Confiança não disponível para esta predição.")

    # Confiança em texto
    st.markdown(f"**Confiança:** {confidence:.1%}")

    # Gráfico de probabilidades
    probabilities = list(prediction['probabilities'])
    if len(probabilities) == 2:
        probabilities.append(0.0)  # padding para classe 'Outro' se modelo antigo

    st.markdown("#### Probabilidades:")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Gato', f"{probabilities[0]:.1%}")
    with col2:
        st.metric('Cachorro', f"{probabilities[1]:.1%}")
    with col3:
        st.metric('Outro', f"{probabilities[2]:.1%}")

    # Barra de progresso dupla
    st.markdown("**Distribuição:**")
    st.bar_chart({
        'Gato': probabilities[0],
        'Cachorro': probabilities[1],
        'Outro': probabilities[2]
    })


if __name__ == "__main__":
    main()
