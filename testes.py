from flyfood_colonia import *
from flyfood_genetico import *
from flyfood_recozimento import *
from auxiliar import plotar_caminho
from typing import List, Tuple, Callable
import random, time, tqdm, math, matplotlib.pyplot as plt
import imageio
from os import listdir, unlink
from os.path import isfile, join
import threading

def gerar_coordenadas_aleatorias(pontos : int = 52, x : int = 1000, y : int = 1000) -> Tuple[Grafo, List[Tuple[int, int]]]:
    # Gerar cordenadas
    cordenadas = [(random.randrange(1, x), random.randrange(1, y)) for _ in range(pontos)]
    # Savar mapa
    with open(f"mapas/{pontos}_pontos", 'w') as f:
        csv.writer(f).writerows(cordenadas)
    # Gerar grafo
    grafo = gerar_grafo(f"mapas/{pontos}_pontos")

    return grafo, cordenadas

def gerar_gif(algoritmo : Callable) -> None:
    # Limpar arquivos
    for arquivo in listdir("figs"):
        unlink(f"./figs/{arquivo}")

    algoritmo(plot=True)
    arquivos = [f for f in listdir("figs") if isfile(join("figs", f))]
    arquivos.sort(key=lambda a: int(a[-8:-4]))
    imagens = []
    for a in arquivos:
        imagens.append(imageio.v2.imread(f"./figs/{a}"))
    imageio.mimsave("gifs/gif.gif", imagens)

def genetico_teste(
        nome_arquivo : str = "berlin52.csv",
        n_populacao : int = 60,
        n_geracoes : int = 2000,
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
    counter = 0

    for _ in (t:= tqdm.trange(n_geracoes)):
        filhos = gerar_filhos(pais, p_mutacao=p_mutacao, p_cruzamento=p_cruzamento)
        pais = selecionar_pais(grafo, filhos)

        t.set_description(f"Distância encontrada : {distancia_caminho(grafo, pais[0])}")

        if tempo < time.process_time_ns() - comeco:
            break
        if plot and counter == 40:
            menor_caminho = min(pais, key=lambda x: distancia_caminho(grafo, x))
            menor_distancia = distancia_caminho(grafo, menor_caminho)
            plotar_caminho(caminho=menor_caminho,
                            dist=menor_distancia, 
                            plotar=False,
                            salvar=True,
                            nome_fig=f"fig_{_:04d}", 
                            titulo="Algoritmo Genético")     
            counter = 0
        counter += 1

    
    menor_caminho = min(pais, key=lambda x: distancia_caminho(grafo, x))

    return distancia_caminho(grafo, menor_caminho), menor_caminho

def colonia_teste(
        mapa = gerar_grafo(),
        C_FEROMONIOS : float = 10.27,
        C_PROXIMIDADE : float = 488.19,
        alfa : float = 1.42, # importância dos feromônios
        beta : float = 1.65, # importância das proximidades
        taxa_evaporacao : float = 0.70,
        feromonios_iniciais :float = 0.19,
        n_geracoes : int = 35,
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

    t = tqdm.trange(n_geracoes)

    for gen in t:
        formigas, distancias = gerar_formigas(mapa, alfa, beta, feromonios, proximidades)
        evaporar_feromonios(feromonios, taxa_evaporacao)
        for n in range(len(formigas)):
            adicionar_feromonios(formigas[n], distancias[n], C_FEROMONIOS, feromonios)
            if distancias[n] < melhor_distancia:
                melhor_rota, melhor_distancia = formigas[n], distancias[n]
        t.set_description(f"Melhor distância : {melhor_distancia}")
    
        if tempo < time.process_time_ns() - comeco:
            break
        if plot:
            plotar_caminho(melhor_rota, dist=melhor_distancia, plotar=False,salvar=True, nome_fig=f"colônia_{gen:02d}", titulo="Colônia de Formigas")

    return melhor_distancia, melhor_rota

def otimizar_rota_teste(localizacoes: List[Tuple[float, float]] = abrir_arquivo(),
                  temp_inicial: float = 1000,
                  temp_minima: float = 1e-8,
                  resfriamento: float = 0.995,
                  iteracoes_por_temp: int = 300,
                  plot : bool = False,
                  tempo : float = float('inf')) -> Tuple[List[int], float]:
    
    comeco = time.process_time_ns()
    tempo *= 10**9

    pontos_para_visitar = list(range(len(localizacoes)))
    pontos_para_visitar.remove(0)

    random.shuffle(pontos_para_visitar)
    caminho_atual = pontos_para_visitar[:]
    distancia_atual = calcular_caminho_total(caminho_atual, localizacoes)

    melhor_caminho = caminho_atual[:]
    melhor_distancia = distancia_atual
    counter = 0

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
        
        if plot and counter % 30 == 0:
            plotar_caminho(caminho=melhor_caminho,
                            dist=melhor_distancia, 
                            plotar=False,
                            salvar=True,
                            nome_fig=f"fig_{counter:04d}", 
                            titulo="Recozimento Simulado")
        counter += 1
        if tempo < time.process_time_ns() - comeco:
            break

        temperatura *= resfriamento
        t.set_description(f"Temperatura : {(temperatura - temp_minima):.5f} | Distânciaa : {melhor_distancia:.5f}")
    t.close()
    return melhor_caminho, melhor_distancia




if __name__ == "__main__": 
    
    """x = [f"{t}s" for t in range(1, 11)]

    res1, res2, res3 = [], [], []
    for t in range(1, 11):
        #res2.append(sum(colonia_teste(n_geracoes=100000, tempo=t)[0] for _ in range(10)) / 10)
        res3.append(sum(otimizar_rota_teste(tempo=t)[1] for _ in range(10)) / 10)"""

    """plt.title("Algoritmo Genético")
    plt.xlabel("Tempo (em segundos)")
    plt.ylabel("Distância")
    plt.ylim(0, 20000)
    plt.bar(x, res1)  
    plt.show()"""

    """plt.title("Colônia de Formiga")
    plt.xlabel("Tempo (em segundos)")
    plt.ylabel("Distância")
    plt.ylim(0, 20000)
    plt.bar(x, res2)
    plt.show()"""

    """plt.title("Recozimento Simulado")
    plt.xlabel("Tempo (em segundos)")
    plt.ylabel("Distância")
    plt.ylim(0, 20000)
    plt.bar(x, res3)
    plt.show()"""

    x = ["Algoritmo Genético", "Recozimento Simulado", "Colônia de Formigas"]

    res = []
    t = 1
    res.append(sum(genetico_teste(tempo=t)[0] for _ in range(10)) / 10)
    res.append(sum(otimizar_rota_teste(tempo=t)[1] for _ in range(10)) / 10)
    res.append(sum(colonia_teste(n_geracoes=100000, tempo=t)[0] for _ in range(10)) / 10)

    plt.ylim(0, 15000)
    plt.title(f"Distância encontrada em {t} segundo")
    plt.ylabel("Distância")
    plt.bar(x, res)
    plt.show()