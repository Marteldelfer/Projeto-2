from auxiliar import abrir_arquivo, distancia, plotar_caminho
from typing import Dict, Tuple, List
import math
import tqdm
import random
import matplotlib.pyplot as plt

def calcular_caminho_total(caminho: List[int], localizacoes: List[Tuple[float, float]]) -> float:

    distancia_total = 0.0
    cidade_atual = 0

    for cidade in caminho:
        x1, y1 = localizacoes[cidade_atual]
        x2, y2 = localizacoes[cidade]
        distancia_total += distancia(x1, y1, x2, y2)
        cidade_atual = cidade
    
    x1, y1 = localizacoes[cidade_atual]
    x2, y2 = localizacoes[0]
    distancia_total += distancia(x1, y1, x2, y2)

    return distancia_total

def otimizar_rota(localizacoes: List[Tuple[float, float]] = abrir_arquivo(),
                  temp_inicial: float = 1000,
                  temp_minima: float = 1e-8,
                  resfriamento: float = 0.995,
                  iteracoes_por_temp: int = 300) -> Tuple[List[int], float]:

    pontos_para_visitar = list(range(len(localizacoes)))
    pontos_para_visitar.remove(0)

    random.shuffle(pontos_para_visitar)
    caminho_atual = pontos_para_visitar[:]
    distancia_atual = calcular_caminho_total(caminho_atual, localizacoes)

    melhor_caminho = caminho_atual[:]
    melhor_distancia = distancia_atual

    temperatura = temp_inicial
    t = tqdm.tqdm()
    while temperatura > temp_minima:
        for _ in range(iteracoes_por_temp):

            novo_caminho = caminho_atual[:]
            i, j = random.sample(range(len(novo_caminho)), 2)
            novo_caminho[i], novo_caminho[j] = novo_caminho[j], novo_caminho[i]
            
            nova_distancia = calcular_caminho_total(novo_caminho, localizacoes)
            diferenca = nova_distancia - distancia_atual

            if diferenca < 0 or random.random() < math.exp(-diferenca / temperatura):
                caminho_atual = novo_caminho[:]
                distancia_atual = nova_distancia

                if distancia_atual < melhor_distancia:
                    melhor_caminho = caminho_atual[:]
                    melhor_distancia = distancia_atual
        
        temperatura *= resfriamento
        t.set_description(f"Temperatura : {(temperatura - temp_minima):.5f} | Distânciaa : {melhor_distancia:.5f}")
    t.close()
    return melhor_distancia, melhor_caminho

if __name__ == "__main__":
    localizacoes = abrir_arquivo("mapas/berlin52.csv")
    melhor_caminho, melhor_distancia = otimizar_rota(localizacoes)
    plotar_caminho(melhor_caminho, localizacoes)