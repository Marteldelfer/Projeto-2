from flyfood_colonia import *
from flyfood_genetico import *
from auxiliar import plotar_caminho
from typing import List, Tuple
import random, time, tqdm, math, matplotlib.pyplot as plt
import imageio

def gerar_coordenadas_aleatorias(pontos : int = 52, x : int = 1000, y : int = 1000) -> Tuple[Grafo, List[Tuple[int, int]]]:
    # Gerar cordenadas
    cordenadas = [(random.randrange(1, x), random.randrange(1, y)) for _ in range(pontos)]
    # Savar mapa
    with open(f"mapas/{pontos}_pontos", 'w') as f:
        csv.writer(f).writerows(cordenadas)
    # Gerar grafo
    grafo = gerar_grafo(f"mapas/{pontos}_pontos")

    return grafo, cordenadas

def genetico_teste(
        nome_arquivo : str = "berlin52.csv",
        n_populacao : int = 100,
        n_geracoes : int = 1000,
        p_mutacao : float = 0.05,
        p_cruzamento : float = 0.90,
        tempo : float = float('inf'),
        plot : bool = False
):
    """
    Código principal, retorna a menor distância e o menor caminho encontrado

    n_populacao -> tamanho de cada população

    n_geracoes -> número de gerações. Quanto mais gerações, maior o tempo do
    algoritmo

    p_mutacao -> chance de mutação para cada filho
    
    p_cruzamento -> chance de de dois pais gerarem filho
    """
    comeco = time.process_time_ns()
    tempo *= 10**9

    grafo = gerar_grafo(nome_arquivo)
    pais = [gerar_caminho_aleatorio(grafo) for _ in range(n_populacao)]

    for _ in (t:= tqdm.trange(n_geracoes)):
        filhos = gerar_filhos(pais, p_mutacao=p_mutacao, p_cruzamento=p_cruzamento)
        pais = selecionar_pais(grafo, filhos)

        t.set_description(f"Distância encontrada : {distancia_caminho(grafo, pais[0])}")

        if tempo < time.process_time_ns() - comeco:
            break
    
    menor_caminho = min(pais, key=lambda x: distancia_caminho(grafo, x))

    return distancia_caminho(grafo, menor_caminho), menor_caminho

def colonia_teste(
        mapa = gerar_grafo(),
        C_FEROMONIOS : float = 5,
        C_PROXIMIDADE : float = 300,
        alfa : float = 2,
        beta : float = 2,
        taxa_evaporacao : float = 0.7,
        feromonios_iniciais :float = 0.5,
        n_geracoes : int = 100,
        tempo : float = float('inf'), # Tempo em segundos
        plot : bool = False
) -> Tuple:
    """
    O algoritmo propriamente dito. Retorna a menor distancia, o menor caminho e um 
    registro de cada geração.
    
    Itera `n_geracoes` vezes, atualizando feromônios a cada geração
    """

    comeco = time.process_time_ns()
    tempo *= 10**9

    proximidades = encontrar_proximidades(mapa, C_PROXIMIDADE)
    feromonios = [[feromonios_iniciais] * i for i in range(len(mapa))]
    melhor_rota, melhor_distancia = [], float('inf')

    log = {}
    t = tqdm.trange(n_geracoes)

    for gen in t:
        formigas, distancias = gerar_formigas(mapa, alfa, beta, feromonios, proximidades)
        log[f"geração{gen}"] = [None] * len(formigas)
        evaporar_feromonios(feromonios, taxa_evaporacao)
        for n in range(len(formigas)):
            log[f"geração{gen}"][n] = (formigas[n], distancias[n]) 
            adicionar_feromonios(formigas[n], distancias[n], C_FEROMONIOS, feromonios)
            if distancias[n] < melhor_distancia:
                melhor_rota, melhor_distancia = formigas[n], distancias[n]
        t.set_description(f"Melhor distância : {melhor_distancia}")
    
        if tempo < time.process_time_ns() - comeco:
            break
        if plot:
            plotar_caminho(melhor_rota, plotar=False,salvar=True, nome_fig=f"genético_{gen}")

    return melhor_distancia, melhor_rota, log


grafo, coordenadas = gerar_grafo(), abrir_arquivo()

dist, rota, log = colonia(grafo)
plotar_caminho(rota, coordenadas)