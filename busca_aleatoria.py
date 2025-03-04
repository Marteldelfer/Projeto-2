from flyfood_colonia import colonia
from flyfood_genetico import genetico
from typing import Callable, Dict, List, Any
from testes import tamanho_grafo
from auxiliar import *
import random

hp_colonia = {
    "C_FEROMONIOS" : (1., 1000., 0),
    "C_PROXIMIDADE" : (1., 1000., 0),
    "alfa" : (0., 10., 0),
    "beta" : (0., 10., 0),
    "taxa_evaporacao" : (0.01, 0.99, 0),
    "feromonios_iniciais" : (0.01, 0.99, 0),
}
hp_genetico = {
    "n_populacao" : (20, 400, 4),
    "n_geracoes" : (100, 4000, 1),
    "p_mutacao" : (0.01, 0.2, 0),
    "p_cruzamento" : (0.1, 0.99, 0)
}
def testar_n(
        algoritmo : Callable[[Any], Tuple[float, List[int]]],
        entrada : Dict[str, Any],
        n : int = 30, #Número de testes
) -> List[Tuple[float, List[int]]]:
    return [algoritmo(**entrada) for _ in range(n)]

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
        melhor_caminho : float,
        iteracoes : int = 50,
        parametros_por_iteracao : int = 10,
        testes_por_parametro : int = 30
) -> Tuple[float, Any]:
    melhor_avaliacao = float('inf')
    melhor_parametros = {}
    melhores = []

    for i in range(iteracoes):
        hiper_parametros = [gerar_entrada(parametros) for _ in range(parametros_por_iteracao)]
        avaliacoes = [avaliar(algoritmo,hp,melhor_caminho,testes_por_parametro) for hp in hiper_parametros]
        melhor = min(zip(avaliacoes, hiper_parametros), key=lambda x: x[0])
        
        if melhor[0] < melhor_avaliacao:
            melhores.append(melhor)
            melhor_avaliacao = melhor[0]
            melhor_parametros = melhor[1]
        print(melhor_avaliacao)
        parametros = rebalancear(parametros, melhor_parametros)

    return min(melhores, key=lambda x: avaliar(algoritmo, x[1], melhor_caminho, 100))

if __name__ == "__main__":
    """
    print(otimizar(colonia, hp_colonia, 7544, 15, 20, 10))
    novo = avaliar(colonia, {'C_FEROMONIOS': 481.61225795933996, 
                      'C_PROXIMIDADE': 479.62752942840694, 
                      'alfa': 1.3884671493840979, 
                      'beta': 1.9807802812405069, 
                      'taxa_evaporacao': 0.6394506283576902, 
                      'feromonios_iniciais': 0.21209498250953987,
                      "n_geracoes" : 75}, 7544, 10)
    antigo = avaliar(colonia, {"n_geracoes" : 75}, 7544, 10)
    print(novo, antigo)
    """
    """
    print(avaliar(genetico, {'n_populacao': 384, 
                             'n_geracoes': 982, 
                             'p_mutacao': 0.07119685197423396, 
                             'p_cruzamento': 0.9067295091499005}, 7544, 15))
    """
    print(avaliar(genetico, {}, 7544, 15))