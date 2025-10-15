import os
import zipfile
from kaggle.api.kaggle_api_extended import KaggleApi

# Inicializar a API do Kaggle
api = KaggleApi()
api.authenticate()

# Baixar o dataset
dataset = 'lakshmi25npathi/online-retail-dataset'
api.dataset_download_files(dataset, path='data', unzip=False)

# Extrair o arquivo ZIP
with zipfile.ZipFile('data/online-retail-dataset.zip', 'r') as zip_ref:
    zip_ref.extractall('data')
