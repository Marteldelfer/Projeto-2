import csv, math, random, matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Iterable

Grafo = Dict[int, Dict[int, float]]

def soma(iteravel : Iterable[float]) -> float:
    res = 0
    for i in iteravel:
        res += i
    return res

def distancia(x1 : float, y1 : float, x2 : float, y2 : float) -> float:
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def abrir_arquivo() -> List[Tuple[float, float]]:
    with open("berlin52.csv") as f:
        b52 = csv.reader(f)
        cordenadas = []
        for linha in b52:
            cordenadas.append((float(linha[0]), float(linha[1])))
    return cordenadas

def gerar_grafo() -> Grafo:
    grafo = dict()
    cordenadas = abrir_arquivo()

    for i, ponto_a in enumerate(cordenadas):
        distancias = dict()
        for j, ponto_b in enumerate(cordenadas):
            if i == j: # Evitar laços
                continue
            distancias[j] = distancia(*ponto_a, *ponto_b)
        grafo[i] = distancias
    return grafo

def distancia_caminho(grafo : Grafo, caminho : List[int]) -> float:
    res = grafo[0][caminho[0]]
    for i in range(1, len(caminho) - 1):
        res += grafo[i][i + 1]
    return res + grafo[caminho[-1]][0]

def gerar_caminho_aleatorio() -> List[int]:
    res = list(range(1,52))
    random.shuffle(res)
    return res

def aptidao(grafo : Grafo, caminho : List[int]) -> float:
    return 1 / distancia_caminho(grafo, caminho)

def selecionar_pais(grafo : Grafo, candidatos : List[List[int]], teste = "aptidao") -> List[List[int]]:
    pais = []

    if teste == "aptidao":
        for _ in range(len(candidatos) // 2):
            aptidoes = [aptidao(grafo, candidato) for candidato in candidatos]
            soma_aptidoes = soma(aptidoes)
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

def gerar_filhos() -> List[List[int]]:
    pass