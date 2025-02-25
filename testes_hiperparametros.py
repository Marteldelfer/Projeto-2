from flyfood_formigas import colonia
from auxiliar import gerar_grafo
import random
import pandas as pd


def variancia(v):
    media = sum(v) / len(v)
    variancia = 0
    for i in v:
        variancia += (i - media)**2
    variancia /= len(v) - 1
    variancia = variancia ** 0.5
    return variancia

def dez_testes(mapa, **hparams):
    valores = []
    for _ in range(10):
        x = colonia(mapa=mapa,
                    C_FEROMONIOS=hparams['C_FEROMONIOS'],
                    C_PROXIMIDADE=hparams['C_PROXIMIDADE'],
                    alfa=hparams['alfa'],
                    beta=hparams['beta'],
                    taxa_evaporacao=hparams['taxa_evaporacao'],
                    feromonios_iniciais=hparams['feromonios_iniciais'],
                    n_geracoes=50)[0]
        valores.append(x)
    
    media = sum(valores) / 10
    return media, variancia(valores)

def teste_aleatorio(mapa, hparams, variancias, min_max):
    novos_hparams = {}
    for p in hparams:
        novos_hparams[p] = random.uniform(max(min_max[p][0],hparams[p] - variancias[p]),
                       min(min_max[p][1],hparams[p] + variancias[p]))
    m, v = dez_testes(mapa, **novos_hparams)
    return m, v, novos_hparams

def atualizar_h(hparams, novos_hparams):
    for p in hparams:
        hparams[p] = novos_hparams[p]

def reduzir_variancias(vars):
    t = 0
    for v in vars:
        vars[v] /= 5
        t += vars[v]


def testes():
    writer = pd.ExcelWriter("testes_hparametros.xlsx", engine='xlsxwriter')
    mapa = gerar_grafo(r"flyfoood\berlin52.csv")
    hparams = {
        'C_FEROMONIOS': 5,
        'C_PROXIMIDADE': 300,
        'alfa': 3,
        'beta': 3,
        'taxa_evaporacao': 0.5,
        'feromonios_iniciais': 0.5,
    }
    variancias = {
        'C_FEROMONIOS': 10,
        'C_PROXIMIDADE': 250,
        'alfa': 3,
        'beta': 3,
        'taxa_evaporacao': 0.5,
        'feromonios_iniciais': 0.5,
    }
    min_max = {
        'C_FEROMONIOS': (1,1000),
        'C_PROXIMIDADE': (1,1000),
        'alfa': (0,10),
        'beta': (0,10),
        'taxa_evaporacao': (0.1,0.9),
        'feromonios_iniciais': (0.1,0.9),
    }

    melhor, h_melhor, vmelhor = float('inf'), {}, 0
    x = 0
    iteracao = 0
    while x < 4:
        iteracao += 1
        n = 0

        tabela = {p:[] for p in hparams}
        tabela['media'] = []
        tabela['variancia'] = []

        while n < 30:
            m, v, param = teste_aleatorio(mapa, hparams, variancias, min_max)
            if m < melhor:
                melhor, h_melhor, vmelhor = m, param, v
            n += 1

            for p in param:
                tabela[p].append(param[p])
            tabela['media'].append(m)
            tabela['variancia'].append(v)
        
        atualizar_h(hparams, h_melhor)
        reduzir_variancias(variancias)
        x += 1

        df = pd.DataFrame(tabela)
        df.to_excel(writer, sheet_name=f'iteracao_{iteracao}', header=[i for i in tabela], index=False)
    print(h_melhor, melhor, vmelhor)
    writer.close()


if __name__ == '__main__':
    testes()
