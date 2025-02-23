from csv import reader
from typing import List, Tuple

def carregar_mapa(nome_arquivo: str = "berlin52.csv") -> List[Tuple[float, float]]:

    with open(nome_arquivo, newline='') as arquivo_csv:
        leitor = reader(arquivo_csv)
        coordenadas = [(float(linha[0]), float(linha[1])) for linha in leitor]
    return coordenadas

def calcular_distancia(x1: float, y1: float, x2: float, y2: float) -> float:

    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5