from auxiliar import gerar_grafo, abrir_arquivo, plotar_caminho,Grafo
from typing import List, Tuple
from random import random, seed
import matplotlib.pyplot as plt
import tqdm

def encontrar_na_tabela(a : int, b : int, tabela : List[List[float]]) -> float:
    return tabela[max(a,b)][min(a,b)]


def proximo_ponto(
        feromonios : List[List[float]], # Matriz de float 
        alfa : float, 
        proximidades : List[List[float]], # Matriz de float 
        beta : float, 
        ponto_atual : int, # Cidade
        pontos : List[int] # Lista de cidades
        ) -> int:
    """
    Encontra o proximo ponto com chance proporcional ao `feromonio^alfa * proximidade^beta`
    """

    possibilidades = [encontrar_na_tabela(ponto_atual,i,feromonios)**alfa * encontrar_na_tabela(ponto_atual,i,proximidades)**beta for i in pontos]
    total = sum(i if i > 0 else 0.001 for i in possibilidades)
    escolha = random()
    n = 0
    for i in range(len(possibilidades)):
        n += possibilidades[i] / total
        if n >= escolha:
            return pontos[i]
    return pontos[-1] # para caso ocorra um erro por aproximação decimal e a escolha seja alta demais.


def encontrar_proximidades(mapa : Grafo) -> Grafo:
    """
    Transforma um grafo de distancis em um grafo de proximidade

    A proximidade de dois pontos é dado por `1 / distancia`
    """

    proximidades = [[0] * i for i in range(len(mapa))]
    for a in range(len(proximidades)):
        for b in range(len(proximidades[a])):
            proximidades[a][b] = 1 / mapa[a][b]
    return proximidades


def adicionar_feromonios(
        formiga : List[int], 
        distancia : float, 
        C_FEROMONIOS : float, 
        feromonios : List[List[float]]
        ) -> None:
    """
    Adiciona feromonios proporcional `C_FEROMONIOS / distancia`
    """
    for i in range(len(formiga)):
        a = formiga[i]
        b = formiga[i-1]
        feromonios[max(a,b)][min(a,b)] += C_FEROMONIOS / distancia


def evaporar_feromonios(
        feromonios : List[List[float]], 
        taxa_evaporacao : float # entre 0 e 1
        ) -> None:
    """Reduz feromonios de acordo com a taxa de evaporação"""
    for a in range(len(feromonios)):
        for b in range(len(feromonios[a])):
            feromonios[a][b] *= taxa_evaporacao


def gerar_formigas(
        mapa : Grafo, 
        alfa : float, 
        beta : float, 
        feromonios : List[List[float]], 
        proximidades : List[List[float]]
        ) -> List[List[int]]:
    """Retorna uma lista de caminhos gerados a partír do feromônios e proximidade"""

    cidades = range(len(mapa))
    formigas = [[i] for i in cidades]
    distancias = [0] * len(formigas)
    for idx, formiga in enumerate(formigas):
        pontos = [i for i in range(len(mapa))]
        pontos.remove(formiga[0])
        while pontos:
            proximo = proximo_ponto(feromonios, alfa, proximidades, beta, formiga[-1], pontos)
            pontos.remove(proximo)
            distancias[idx] += mapa[formiga[-1]][proximo]
            formiga.append(proximo)
        distancias[idx] += mapa[formiga[0]][formiga[-1]]
    return formigas, distancias


def colonia(
        mapa = gerar_grafo(),
        C_FEROMONIOS : float = 10.27,
        alfa : float = 1.42, # importância dos feromônios
        beta : float = 1.65, # importância das proximidades
        taxa_evaporacao : float = 0.70,
        feromonios_iniciais :float = 0.19,
        n_geracoes : int = 50
) -> Tuple[float, List[int]]:
    """
    O algoritmo propriamente dito. Retorna a menor distancia, o menor caminho e um 
    registro de cada geração.

    Itera `n_geracoes` vezes, atualizando feromônios a cada geração
    """

    proximidades = encontrar_proximidades(mapa)
    feromonios = [[feromonios_iniciais] * i for i in range(len(mapa))]
    melhor_rota, melhor_distancia = [], float('inf')

    t = tqdm.trange(n_geracoes)

    for gen in t:
        formigas, distancias = gerar_formigas(mapa, alfa, beta, feromonios, proximidades)
        evaporar_feromonios(feromonios, taxa_evaporacao)
        for n in range(len(formigas)):
            adicionar_feromonios(formigas[n], distancias[n], C_FEROMONIOS, feromonios)
            if distancias[n] < melhor_distancia:
                melhor_rota, melhor_distancia = formigas[n], distancias[n]
        t.set_description(f"Melhor distância : {melhor_distancia:0.4f}")
    
    return melhor_distancia, melhor_rota


if __name__ == "__main__":
    s = 0.11787129513243644 # melhor resultado encontrado
    seed(s)
    distancia, melhor = colonia()
    plotar_caminho(melhor, abrir_arquivo(),titulo=distancia)
