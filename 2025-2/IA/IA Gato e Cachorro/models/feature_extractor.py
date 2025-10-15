"""
Módulo de extração de features para imagens
Inclui:
- Histogramas de cor RGB (bins=16 por canal)
- HOG (Histogram of Oriented Gradients) usando skimage
"""

from __future__ import annotations

import cv2
import numpy as np
from skimage.feature import hog, local_binary_pattern

__all__ = [
    "extract_color_histogram",
    "extract_hog",
    "extract_features",
]


def extract_color_histogram(image: np.ndarray, bins: int = 16) -> np.ndarray:
    """Extrai histogramas RGB concatenados."""
    # image deve estar em escala 0-1 ou 0-255, não importa para histograma normalizado
    hist_features = []
    for channel in range(3):
        hist = cv2.calcHist([image.astype(np.uint8)], [channel], None, [bins], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        hist_features.extend(hist)
    return np.array(hist_features, dtype=np.float32)


def extract_hog(image: np.ndarray, pixels_per_cell: tuple[int, int] = (8, 8), cells_per_block: tuple[int, int] = (2, 2)) -> np.ndarray:
    """Extrai descritor HOG com parâmetros ajustados."""
    gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    hog_features = hog(
        gray,
        pixels_per_cell=(4, 4),
        cells_per_block=(3, 3),
        orientations=12,
        block_norm="L2-Hys",
        visualize=False,
        feature_vector=True,
    )
    return hog_features.astype(np.float32)


def extract_hsv_histogram(image: np.ndarray, bins: int = 16) -> np.ndarray:
    """Histograma concatenado de HSV."""
    hsv = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGB2HSV)
    hist_features = []
    for channel in range(3):
        hist = cv2.calcHist([hsv], [channel], None, [bins], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        hist_features.extend(hist)
    return np.array(hist_features, dtype=np.float32)


def extract_lbp(image: np.ndarray, P: int = 8, R: int = 1) -> np.ndarray:
    """Local Binary Pattern do canal de luminosidade."""
    gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    lbp = local_binary_pattern(gray, P, R, method="uniform")
    # Histograma LBP
    (hist, _) = np.histogram(lbp.ravel(), bins=np.arange(0, P + 3), range=(0, P + 2))
    hist = hist.astype("float")
    hist /= (hist.sum() + 1e-6)
    return hist

def extract_features(image: np.ndarray) -> np.ndarray:
    """Extrai e concatena todas as features disponíveis."""
    color = extract_color_histogram((image * 255).astype(np.uint8))
    hsv = extract_hsv_histogram((image * 255).astype(np.uint8))
    hog_feat = extract_hog(image)
    lbp_feat = extract_lbp(image)
    return np.concatenate([color, hsv, hog_feat, lbp_feat])
