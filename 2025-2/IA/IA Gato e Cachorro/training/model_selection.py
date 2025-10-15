"""
Script para seleção de modelo: compara vários algoritmos clássicos (RandomForest, SVM RBF,
GradientBoosting, KNN) via GridSearchCV e salva o melhor.
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

import joblib
import numpy as np
from tqdm.auto import tqdm
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier

# Diretórios
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "data" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    X = np.load(PROCESSED_DIR / "features.npy")
    y = np.load(PROCESSED_DIR / "labels.npy")
    return X, y


def build_search_spaces():
    return {
        "RandomForest": {
            "estimator": RandomForestClassifier(random_state=42),
            "param_grid": {
                "n_estimators": [100, 200],
                "max_depth": [None, 10, 20],
            },
        },
        "SVM-RBF": {
            "estimator": SVC(kernel="rbf", probability=True),
            "param_grid": {
                "C": [1, 10],
                "gamma": ["scale", 0.01, 0.001],
            },
        },
        "GradientBoosting": {
            "estimator": GradientBoostingClassifier(random_state=42),
            "param_grid": {
                "n_estimators": [100, 200],
                "learning_rate": [0.1, 0.05],
                "max_depth": [3, 5],
            },
        },
        "KNN": {
            "estimator": KNeighborsClassifier(),
            "param_grid": {
                "n_neighbors": [3, 5, 7],
                "weights": ["uniform", "distance"],
            },
        },
    }


def evaluate_best_models(results):
    metrics = {}
    for name, res in results.items():
        best_est = res["best_estimator"]
        y_pred = res["cv_results"]["y_test_pred"]
        y_true = res["cv_results"]["y_test_true"]
        acc = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)
        metrics[name] = {"accuracy": acc, "f1": f1}
    return metrics


def main():
    print("🚀 Iniciando seleção de modelo...")
    X, y = load_data()
    print(f"📊 Dados carregados: {X.shape[0]} amostras, {X.shape[1]} features")

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    search_spaces = build_search_spaces()
    all_results = {}

    for model_name, cfg in tqdm(search_spaces.items(), desc="Modelos", unit="model"):
        print(f"\n🔍 Avaliando {model_name}")
        grid = GridSearchCV(
            estimator=cfg["estimator"],
            param_grid=cfg["param_grid"],
            cv=skf,
            scoring="accuracy",
            n_jobs=1,
            verbose=0,
            return_train_score=False,
        )
        grid.fit(X, y)
        best = grid.best_estimator_
        print(f"  ✅ Melhor params: {grid.best_params_} -> Acc={grid.best_score_:.4f}")
        all_results[model_name] = {
            "best_estimator": best,
            "best_score": grid.best_score_,
            "best_params": grid.best_params_,
            "cv_results": None,
        }

    # Selecionar melhor
    best_model_name = max(all_results, key=lambda n: all_results[n]["best_score"])
    best_model = all_results[best_model_name]["best_estimator"]
    best_score = all_results[best_model_name]["best_score"]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = MODELS_DIR / f"{best_model_name}_{timestamp}.joblib"
    joblib.dump(best_model, model_path)
    print(f"\n🎉 Melhor modelo: {best_model_name} salvo em {model_path}")

    # Salvar métricas
    metrics = {
        "model_name": best_model_name,
        "best_score": best_score,
        "models": {
            name: {"score": res["best_score"], "params": res["best_params"]}
            for name, res in all_results.items()
        },
    }
    metrics_path = MODELS_DIR / f"{best_model_name}_{timestamp}_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"📄 Métricas salvas em {metrics_path}")


if __name__ == "__main__":
    main()
