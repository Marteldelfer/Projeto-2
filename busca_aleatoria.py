from flyfood_colonia import *
from flyfood_genetico import *
from typing import Callable, Dict, List, Any
from testes import tamanho_grafo
from auxiliar import *
from abrir_tsplib import e_numero
import random
import os

hp_colonia = {
    "C_FEROMONIOS" : (1., 1000., 0),
    "alfa" : (0., 10., 0),
    "beta" : (0., 10., 0),
    "taxa_evaporacao" : (0.01, 0.99, 0),
    "feromonios_iniciais" : (0.01, 0.99, 0),
}
hp_genetico = {
    "n_populacao" : (20, 400, 4),
    "p_mutacao" : (0.01, 0.2, 0),
    "p_cruzamento" : (0.5, 0.99, 0),
    "tempo" : (19.999, 20, 0)
}

def ler_caminho(a : str) -> List[int]:
    a = a[:-4] + ".opt.tour"
    with open(f"tsplib/{a}") as f:
        res = []
        for l in f.readlines():
            try:
                if not e_numero(l.split()[0]):
                    continue
                res.extend([int(i) - 1 for i in l.split()])
            except:
                break
    return res[:-1]

def testar_n(
        algoritmo : Callable[[Any], Tuple[float, List[int]]],
        entrada : Dict[str, Any],
        n : int = 30, #Número de testes
) -> List[Tuple[float, List[int]]]:
    return [algoritmo(**entrada) for _ in range(n)]

def testar_multiplos_mapas(
        algoritmo : Callable[[Any], Tuple[float, List[int]]],
        entrada : Dict[str, Any],
        mapas : List[str], # Nomes dos arquivos dos mapas
) -> List[Tuple[float, List[int]]]:
    return [algoritmo(mapa=gerar_grafo(f"mapas/{mapa}"), **entrada) for mapa in mapas]

def avaliar(
        algoritmo : Callable[[Any], Tuple[float, List[int]]],
        entrada : Dict[str, Tuple[Any, Any]],
        melhor_caminho : float,
        n : int = 30, #Número de testes
) -> float:
    """Média do algoritmo dividido pelo melhor caminho. Um resultado proximo de 1 é ideal"""
    soma = 0
    for res in testar_n(algoritmo, entrada, n):
        soma += res[0]
    return soma / n / melhor_caminho

def avaliar_multiplos_mapas(
        algoritmo : Callable[[Any], Tuple[float, List[int]]],
        entrada : Dict[str, Any],
        mapas : List[str], # Nomes dos arquivos dos mapas
        otimos : List[float]
) -> List[float]:
    res = testar_multiplos_mapas(algoritmo, entrada, mapas)
    return sum(r[0] / o for r, o in zip(res, otimos)) / len(otimos)

def gerar_entrada(
        parametros : Dict[str, Tuple[Any, Any]] # Tuple(min, max)
) -> Dict[str, Any]:
    entrada = dict()
    for parametro, min_max in parametros.items():
        if isinstance(min_max, tuple):
            minimo, maximo, passo = min_max
            if isinstance(minimo, int):
                entrada[parametro] = random.randrange(minimo, maximo + 1, passo)
            else: # É float
                entrada[parametro] = random.uniform(minimo, maximo)
        else:
            entrada[parametro] = min_max
    return entrada

def rebalancear(
        parametros : Dict[str, Tuple[Any, Any]], # Tuple[min e max]
        melhor_parametros : Dict[str, Tuple[Any, Any]],
        CONST : float = 0.15
) -> Dict[str, Tuple[Any, Any]]:
    res = dict()

    for parametro, valor in melhor_parametros.items():
        if not (isinstance(valor, float) or isinstance(valor, int)):
            continue
        mod = (parametros[parametro][1] - parametros[parametro][0]) * CONST
        if isinstance(valor, int):
            mod = int((mod // parametros[parametro][2]) * 4)
        meio = (parametros[parametro][1] + parametros[parametro][0]) / 2
        if valor > meio:
            minimo = parametros[parametro][0] + mod
            maximo = parametros[parametro][1]
        else:
            minimo = parametros[parametro][0]
            maximo = parametros[parametro][1] - mod
        res[parametro] = (minimo, maximo, parametros[parametro][2])
    return res

def otimizar(
        algoritmo :  Callable[[Any], Tuple[float, List[int]]],
        parametros : Dict[str, Tuple[Any, Any, Any]], # Tuple[min e max]
        iteracoes : int = 5,
        parametros_por_iteracao : int = 15,
        mapas : List[str] = ["berlin52.csv"],
        otimos : List[float] = [7544]
) -> Tuple[float, Any]:
    melhor_avaliacao = float('inf')
    melhor_parametros = {}
    melhores = []

    with open(f"teste_hp_{algoritmo.__name__}.txt", "w", buffering=1) as f:
        for i in range(iteracoes):
            hiper_parametros = [gerar_entrada(parametros) for _ in range(parametros_por_iteracao)]
            avaliacoes = [avaliar_multiplos_mapas(algoritmo,hp, mapas, otimos) for hp in hiper_parametros]
            melhor = min(zip(avaliacoes, hiper_parametros), key=lambda x: x[0])
            
            for av, hp in zip(avaliacoes, hiper_parametros):
                f.write(f"{av},{hp}\n")
                 
            if melhor[0] < melhor_avaliacao:
                melhores.append(melhor)
                melhor_avaliacao = melhor[0]
                melhor_parametros = melhor[1]
            print(melhor_avaliacao)
            parametros = rebalancear(parametros, melhor_parametros)

    return min(melhores, key=lambda x: sum(avaliar_multiplos_mapas(algoritmo, x[1], mapas, otimos) for _ in range(10)))

if __name__ == "__main__":
    mapas =  [
        "eil51.csv",
        "ulysses22.csv",
        "att48.csv",
        "eil76.csv",
        "pr76.csv",
        "ulysses16.csv",
        "gr96.csv",
        "berlin52.csv",
        "st70.csv"
        ]
    otimos = [distancia_caminho(gerar_grafo(f"mapas/{a}"), ler_caminho(a)) for a in mapas]
    
    #print(otimizar(colonia, hp_colonia, mapas=mapas, otimos=otimos))
    print(otimizar(genetico, hp_genetico, mapas=mapas, otimos=otimos))

    """
    antigo = (sum(avaliar_multiplos_mapas(colonia, {}, mapas, otimos) for _ in range(10)) / 10)
    novo = (sum(avaliar_multiplos_mapas(colonia, {'C_FEROMONIOS': 279.18660556846885,
                                                    'C_PROXIMIDADE': 582.0445347782235, 
                                                    'alfa': 1.183215578065937, 
                                                    'beta': 2.1146126462807024, 
                                                    'taxa_evaporacao': 0.3351264058783061, 
                                                    'feromonios_iniciais': 0.42754898056821233
                                                    }, mapas, otimos) for _ in range(10)) / 10)
    print(antigo, novo)
    """
