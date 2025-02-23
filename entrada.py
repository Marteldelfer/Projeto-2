import matplotlib.pyplot as plt
from csv import reader
from typing import List, Tuple
Grafo = List[List[float]]

def plotar_caminho(caminho, arquivo = "berlin52.csv", plotar = True, salvar = False, nome_fig = "fig"):
    data = abrir_arquivo()
    for x,y in data:
        plt.scatter(x,y, c="black", s=16)
    for i in range(len(caminho)):
        plt.plot([data[caminho[i]][0], data[caminho[i-1]][0]], [data[caminho[i]][1], data[caminho[i-1]][1]], c = "black")
    if plotar:
        plt.show()
    if salvar:
        plt.savefig(f"./figs/{nome_fig}")
    plt.clf()

def abrir_arquivo(nome_arquivo : str = "berlin52.csv") -> List[Tuple[float, float]]:
    """Abre um arquivo csv e retorna uma lista de cordenadas [(x1,y1), ..., (xn,yn)]"""
    with open(nome_arquivo) as f:
        b52 = reader(f)
        cordenadas = []
        for linha in b52:
            cordenadas.append((float(linha[0]), float(linha[1])))
    return cordenadas

def distancia(x1 : float, y1 : float, x2 : float, y2 : float) -> float:
    """Calcula a distância euclidiana entre dois pontos"""
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def gerar_grafo(nome_arquivo : str = "berlin52.csv") -> Grafo:
    """
    Transforma o arquivo em grafo de distâncias (List[List[float]])
    
    Para acessar a distância entre dois pontos A e B, basta acessar
    `grafo[A][B]`, sendo A e B inteiros
    """
    grafo = []
    cordenadas = abrir_arquivo(nome_arquivo)

    for ponto_a in cordenadas:
        distancias = []
        for ponto_b in cordenadas:
            distancias.append(distancia(*ponto_a, *ponto_b))
        grafo.append(distancias)
    return grafo
