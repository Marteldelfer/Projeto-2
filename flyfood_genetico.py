import csv, math, random, matplotlib.pyplot as plt, numpy as np
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

def trocar_gene(caminho : List[int], indicie : int, gene : int) -> None:
    for i in range(len(caminho)):
        if caminho[i] == gene:
            indicie_trocar = i
            break
    caminho[indicie], caminho[indicie_trocar] = caminho[indicie_trocar], caminho[indicie]

def crossover(a : List[int], b : List[int]) -> Tuple[List[int], List[int]]:
    indicie_troca = random.randrange(0, len(a))
    res_a, res_b = a[:], b[:]
    for i in range(indicie_troca):
        trocar_gene(res_a, i, b[i])
        trocar_gene(res_b, i, a[i])
    return res_a, res_b

def mutacao(caminho : List[int], p : float = 0.1) -> None:
    if p >= random.random():
        i_gene_a, i_gene_b = random.randrange(len(caminho)), random.randrange(len(caminho))
        caminho[i_gene_a], caminho[i_gene_b] = caminho[i_gene_b], caminho[i_gene_a]

def gerar_filhos(pais : List[List[int]], p_mutacao : float = 0.1, p_filho : float = 0.95) -> List[List[int]]:
    filhos = []
    while pais:
        pai_a = pais.pop(random.randrange(0, len(pais)))
        pai_b = pais.pop(random.randrange(0, len(pais)))
        if p_filho >= random.random():
            filhos.extend(crossover(pai_a, pai_b))
            filhos.extend(crossover(pai_a, pai_b))
        else:
            filhos.extend((pai_a,pai_b,pai_a,pai_b))
    for filho in filhos:
        mutacao(filho, p_mutacao)
    return filhos

def genetico():
    grafo = gerar_grafo()
    pais = [gerar_caminho_aleatorio() for _ in range(40)]
    for _ in range(500):
        filhos = gerar_filhos(pais)
        pais = selecionar_pais(grafo, filhos, teste="torneio")
    return pais

def plotar_caminho(caminho):
    data = abrir_arquivo()
    for x,y in data:
        plt.scatter(x,y, c="black", s=16)
    caminho = gerar_caminho_aleatorio()
    for a, b in zip(caminho, caminho[1:]):
        plt.plot([data[a][0], data[b][0]], [data[a][1], data[b][1]], c = "black")
    plt.show()


print(distancia_caminho(gerar_grafo(), min(genetico(), key=lambda x: distancia_caminho(gerar_grafo(), x))))
print(distancia_caminho(gerar_grafo(), min(genetico(), key=lambda x: distancia_caminho(gerar_grafo(), x))))
print(distancia_caminho(gerar_grafo(), min(genetico(), key=lambda x: distancia_caminho(gerar_grafo(), x))))
print(distancia_caminho(gerar_grafo(), min(genetico(), key=lambda x: distancia_caminho(gerar_grafo(), x))))

plotar_caminho(min(genetico(), key=lambda x: distancia_caminho(gerar_grafo(), x)))
plotar_caminho(min(genetico(), key=lambda x: distancia_caminho(gerar_grafo(), x)))
plotar_caminho(min(genetico(), key=lambda x: distancia_caminho(gerar_grafo(), x)))
plotar_caminho(min(genetico(), key=lambda x: distancia_caminho(gerar_grafo(), x)))

