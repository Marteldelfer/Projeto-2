from auxiliar import abrir_arquivo, distancia
from typing import Dict, Tuple, List
import math
import tqdm
import random
import matplotlib.pyplot as plt

def preparar_localizacoes(nome_arquivo: str = "berlin52.csv") -> Dict[str, Tuple[float, float]]:
 
    coordenadas = abrir_arquivo(nome_arquivo)
    localizacoes = {str(i+1): coordenadas[i] for i in range(len(coordenadas))}
    return localizacoes

def calcular_caminho_total(caminho: List[str], localizacoes: Dict[str, Tuple[float, float]]) -> float:

    distancia_total = 0.0
    cidade_atual = "1"  

    for cidade in caminho:
        x1, y1 = localizacoes[cidade_atual]
        x2, y2 = localizacoes[cidade]
        distancia_total += distancia(x1, y1, x2, y2)
        cidade_atual = cidade
    
    x1, y1 = localizacoes[cidade_atual]
    x2, y2 = localizacoes["1"]
    distancia_total += distancia(x1, y1, x2, y2)

    return distancia_total

def otimizar_rota(localizacoes: Dict[str, Tuple[float, float]],
                  temp_inicial: float = 1000,
                  temp_minima: float = 1e-8,
                  resfriamento: float = 0.995,
                  iteracoes_por_temp: int = 300) -> Tuple[List[str], float]:

    pontos_para_visitar = list(localizacoes.keys())
    pontos_para_visitar.remove("1")

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
    return melhor_caminho, melhor_distancia

def exibir_rota(caminho: List[str], localizacoes: Dict[str, Tuple[float, float]], distancia: float):

    caminho_completo = ["1"] + caminho + ["1"]  
    x_coords, y_coords = [], []

    for cidade in caminho_completo:
        x, y = localizacoes[cidade]
        x_coords.append(x)
        y_coords.append(y)

    plt.figure(figsize=(8, 6))
    plt.title(f"{distancia:.2f}")

    for (x, y) in localizacoes.values():
        plt.scatter(x, y, c="black", s=16)

    plt.plot(x_coords, y_coords, c="black", lw=1)

    plt.xlabel("Coordenada X")
    plt.ylabel("Coordenada Y")
    plt.show()

if __name__ == "__main__":
    localizacoes = preparar_localizacoes("berlin52.csv")
    melhor_caminho, melhor_distancia = otimizar_rota(localizacoes)
    exibir_rota(melhor_caminho, localizacoes, melhor_distancia)