import pandas as pd

vendas = pd.DataFrame({
    "Produto": ["Notebook", "Mouse", "Teclado", "Monitor", "Mouse", "Notebook", "Headset"],
    "Quantidade": [2, 10, 5, 3, 7, 1, 4],
    "Preço": [3500, 80, 120, 900, 85, 3600, 250],
    "Data": [
        "2023-09-01", "2023-09-01", "2023-08-30",
        "2023-09-01", "2023-09-02", "2023-08-29", "2023-09-01"
    ]
})

filtro = vendas[vendas["Data"] == "2023-09-01"]

print("Vendas em 2023-09-01:")
print(filtro)
