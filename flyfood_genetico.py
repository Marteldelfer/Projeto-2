import csv, math, random, matplotlib.pyplot as plt, numpy as np
from typing import List, Tuple, Dict, Iterable

Grafo = Dict[int, Dict[int, float]]

def abrir_arquivo(nome_arquivo : str = "berlin52.csv") -> List[Tuple[float, float]]:
    with open(nome_arquivo) as f:
        b52 = csv.reader(f)
        cordenadas = []
        for linha in b52:
            cordenadas.append((float(linha[0]), float(linha[1])))
    return cordenadas

def gerar_grafo(nome_arquivo : str = "berlin52.csv", aleatorio=False,tam=52) -> Grafo:
    grafo = dict()
    if not aleatorio:
        cordenadas = abrir_arquivo(nome_arquivo)
    else:
        cordenadas = [(random.randint(1,1000), random.randint(1,1000)) for _ in range(tam)]

    for i, ponto_a in enumerate(cordenadas):
        distancias = dict()
        for j, ponto_b in enumerate(cordenadas):
            if i == j: # Evitar laços
                continue
            distancias[j] = distancia(*ponto_a, *ponto_b)
        grafo[i] = distancias
    return grafo

def distancia(x1 : float, y1 : float, x2 : float, y2 : float) -> float:
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def distancia_caminho(grafo : Grafo, caminho : List[int]) -> float:
    res = grafo[0][caminho[0]]
    for i in range(1, len(caminho) - 1):
        res += grafo[i][i + 1]
    return res + grafo[caminho[-1]][0]

def gerar_caminho_aleatorio(grafo : Grafo) -> List[int]:
    res = list(range(1,len(grafo)))
    random.shuffle(res)
    return res

def aptidao(grafo : Grafo, caminho : List[int]) -> float:
    return 1 / distancia_caminho(grafo, caminho)

def selecionar_pais(grafo : Grafo, candidatos : List[List[int]], teste = "torneio") -> List[List[int]]:
    pais = []

    if teste == "aptidao":
        for _ in range(len(candidatos) // 2):
            aptidoes = [aptidao(grafo, candidato) for candidato in candidatos]
            soma_aptidoes = sum(aptidoes)
            aptidoes = [i / soma_aptidoes for i in aptidoes]
            chance = random.random()

            for index, i in enumerate(aptidoes):
                if i > chance:
                    pais.append(candidatos.pop(index))
                    break
                chance -= i
        return pais

    elif teste == "torneio":
        pais = []
        for _ in range(len(candidatos) // 2):
            candidatoA = candidatos.pop(random.randrange(0, len(candidatos)))
            candidatoB = candidatos.pop(random.randrange(0, len(candidatos)))
            pais.append(candidatoA if distancia_caminho(grafo, candidatoA) < distancia_caminho(grafo, candidatoB) else candidatoB)
        return pais

def pmx(caminho_a : List[int], caminho_b : List[int], separador : int) -> Tuple[List[int], List[int]]:

    for indicie_a, gene_a in enumerate(caminho_a[:separador]):
        for indicie_b, gene_b in enumerate(caminho_b):
            if gene_a == gene_b:
                caminho_b[indicie_a], caminho_b[indicie_b] = caminho_b[indicie_b], caminho_b[indicie_a]
    return caminho_a, caminho_b 

def crossover(pai_a : List[int], pai_b : List[int]) -> Tuple[List[int], List[int]]:
    separador = random.randrange(0, len(pai_a))
    a, b = pmx(pai_a, pai_b, separador)
    filho_a = a[:separador] + b[separador:]
    filho_b = b[:separador] + a[separador:]
    return filho_a, filho_b

def mutacao(caminho : List[int], p : float = 0.1) -> None:
    for i in range(len(caminho)):
        if p >= random.random():
            i_gene = random.randrange(len(caminho))
            caminho[i_gene], caminho[i] = caminho[i], caminho[i_gene]

def gerar_filhos(pais : List[List[int]], p_mutacao : float = 0.1, p_filho : float = 0.95) -> List[List[int]]:
    filhos = []
    while pais:
        pai_a = pais.pop(random.randrange(0, len(pais)))
        pai_b = pais.pop(random.randrange(0, len(pais)))
        if p_filho >= random.random():
            filhos.extend(crossover(pai_a, pai_b))
            filhos.extend(crossover(pai_b, pai_a))
        else:
            filhos.extend((pai_a,pai_b,pai_a,pai_b))
    for filho in filhos:
        mutacao(filho, p_mutacao)
    return filhos

def genetico(
        nome_arquivo : str = "berlin52.csv",
        n_populacao : int = 40,
        n_geracoes : int = 1000,
        p_mutacao : float = 0.05,
        p_cruzamento : float = 0.90,
        teste = "torneio",
        aleatorio : bool = False
):
    grafo = gerar_grafo(nome_arquivo, aleatorio=aleatorio)
    pais = [gerar_caminho_aleatorio(grafo) for _ in range(n_populacao)]

    for _ in range(n_geracoes):
        filhos = gerar_filhos(pais, p_mutacao=p_mutacao, p_filho=p_cruzamento)
        pais = selecionar_pais(grafo, filhos, teste)
    
    menor_caminho = min(pais, key=lambda x: distancia_caminho(grafo, x))
    return distancia_caminho(grafo, menor_caminho), menor_caminho

def plotar_caminho(caminho):
    data = abrir_arquivo()
    for x,y in data:
        plt.scatter(x,y, c="black", s=16)
    for a, b in zip(caminho, caminho[1:]):
        plt.plot([data[a][0], data[b][0]], [data[a][1], data[b][1]], c = "black")
    plt.show()


if __name__ == "__main__":
    d, caminho = genetico()
    print(f"{d}\n{caminho}")