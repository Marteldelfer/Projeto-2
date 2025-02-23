import csv, math, random, tqdm, matplotlib.pyplot as plt, numpy as np
from auxiliar import plotar_caminho, gerar_grafo, distancia_caminho, abrir_arquivo
from typing import List, Tuple

Grafo = List[List[float]]


def gerar_caminho_aleatorio(grafo : Grafo) -> List[int]:
    """Gera um caminho aleátorio dentro de um grafo"""
    res = list(range(0,len(grafo)))
    random.shuffle(res)
    return res

def selecionar_pais(grafo : Grafo, candidatos : List[List[int]]) -> List[List[int]]:
    """
    Retorna uma lista de caminhos pais para um algoritmo genético

    Os caminhos são selecionados via torneio
    """
    pais = []
    for _ in range(len(candidatos) // 2):
        candidatoA = candidatos.pop(random.randrange(0, len(candidatos)))
        candidatoB = candidatos.pop(random.randrange(0, len(candidatos)))
        pais.append(candidatoA if distancia_caminho(grafo, candidatoA) < distancia_caminho(grafo, candidatoB) else candidatoB)
    return pais

def trocar(filho : List[int], indicie : int, gene : int) -> None:
    """Função auxiliar, coloca um elemento em `gene` em `filho[indicie]`"""
    for i, g in enumerate(filho):
        if gene == g:
            filho[indicie], filho[i] = filho[i], filho[indicie]
            break 

def pmx(caminho_a : List[int], caminho_b : List[int]) -> Tuple[List[int], List[int]]:
    """Função auxiliar, retorna os filhos gerados pelo cruzamento de dois pais"""
    separador = random.randrange(0, len(caminho_a))
    filho_a = caminho_a[:]
    filho_b = caminho_b[:]
    filho_c = caminho_a[::-1]
    filho_d = caminho_b[::-1]

    for i, gene in enumerate(caminho_a[:separador]):
        trocar(filho_b, i, gene)    
    for i, gene in enumerate(caminho_b[:separador]):
        trocar(filho_a, i, gene)
    for i, gene in enumerate(caminho_a[::-1][:separador]):
        trocar(filho_d, i, gene)
    for i, gene in enumerate(caminho_b[::-1][:separador]):
        trocar(filho_c, i, gene)
    
    return filho_a, filho_b, filho_c, filho_d
        

def mutacao(caminho : List[int], p : float = 0.1) -> None:
    """Troca dois genes aleatórios com probabilidade p"""
    if p > random.random():
        i_a, i_b = (random.randrange(0, len(caminho)) for _ in range(2))
        caminho[i_a], caminho[i_b] = caminho[i_b], caminho[i_a]

def gerar_filhos(pais : List[List[int]], p_mutacao : float = 0.1, p_cruzamento : float = 0.95) -> List[List[int]]:
    """
    Gera uma geração de filhos para o algoritmo genético
    
    p_mutacao -> chance de mutação para cada filho

    p_cruzamento -> chance de de dois pais gerarem filho
    """
    filhos = []
    while pais:
        pai_a = pais.pop(random.randrange(0, len(pais)))
        pai_b = pais.pop(random.randrange(0, len(pais)))
        if p_cruzamento >= random.random():
            filhos.extend(pmx(pai_a, pai_b))
        else:
            filhos.extend((pai_a,pai_b,pai_a,pai_b))
            
    for filho in filhos:
        mutacao(filho, p_mutacao)
    return filhos

def genetico(
        nome_arquivo : str = "berlin52.csv",
        n_populacao : int = 60,
        n_geracoes : int = 2000,
        p_mutacao : float = 0.05,
        p_cruzamento : float = 0.90,
):
    """
    Código principal, retorna a menor distância e o menor caminho encontrado

    n_populacao -> tamanho de cada população

    n_geracoes -> número de gerações. Quanto mais gerações, maior o tempo do
    algoritmo

    p_mutacao -> chance de mutação para cada filho
    
    p_cruzamento -> chance de de dois pais gerarem filho
    """
    grafo = gerar_grafo(nome_arquivo)
    pais = [gerar_caminho_aleatorio(grafo) for _ in range(n_populacao)]

    for _ in (t:= tqdm.trange(n_geracoes)):
        filhos = gerar_filhos(pais, p_mutacao=p_mutacao, p_cruzamento=p_cruzamento)
        pais = selecionar_pais(grafo, filhos)
        t.set_description(str(distancia_caminho(grafo, pais[0])))
    
    menor_caminho = min(pais, key=lambda x: distancia_caminho(grafo, x))
    return distancia_caminho(grafo, menor_caminho), menor_caminho

if __name__ == "__main__":
    d, caminho = genetico()
    cordenadas = abrir_arquivo()

    print(f"{d}  {caminho}")
    plotar_caminho(caminho, cordenadas, titulo=d)