from entrada import gerar_grafo, abrir_arquivo
from random import random
import matplotlib.pyplot as plt

mapa = gerar_grafo(r"flyfoood\berlin52.csv")

def encontrar_na_tabela(a,b,tabela):
    return tabela[max(a,b)][min(a,b)]


def proximo_ponto(feromonios, alfa, proximidades, beta, ponto_atual, pontos):
    possibilidades = [encontrar_na_tabela(ponto_atual,i,feromonios)**alfa * encontrar_na_tabela(ponto_atual,i,proximidades)**beta for i in pontos]
    total = sum(possibilidades)
    escolha = random()
    n = 0
    for i in range(len(possibilidades)):
        n += possibilidades[i] / total
        if n >= escolha:
            return pontos[i]
    return pontos[-1] # para caso ocorra um erro por aproximação decimal e a escolha seja alta demais.


def encontrar_proximidades(mapa, Constante):
    proximidades = [[0] * i for i in range(len(mapa))]
    for a in range(len(proximidades)):
        for b in range(len(proximidades[a])):
            proximidades[a][b] = Constante / mapa[a][b]
    return proximidades


def adicionar_feromonios(formiga, distancia, Constante_feromonios, feromonios):
    for i in range(len(formiga)):
        a = formiga[i]
        b = formiga[i-1]
        feromonios[max(a,b)][min(a,b)] += Constante_feromonios / distancia


def evaporar_feromonios(feromonios, taxa_evaporacao):
    for a in range(len(feromonios)):
        for b in range(len(feromonios[a])):
            feromonios[a][b] *= taxa_evaporacao


def gerar_formigas(mapa, alfa, beta, feromonios, proximidades):
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


def colonia(mapa, Constante_feromonios, Constante_proximidade, alfa, beta, taxa_evaporacao, feromonios_iniciais, qnt_geracoes):

    proximidades = encontrar_proximidades(mapa, Constante_proximidade)
    feromonios = [[feromonios_iniciais] * i for i in range(len(mapa))]
    melhor_rota, melhor_distancia = [], float('inf')

    log = {}

    for gen in range(qnt_geracoes):
        formigas, distancias = gerar_formigas(mapa, alfa, beta, feromonios, proximidades)
        log[f"geração{gen}"] = [None] * len(formigas)
        evaporar_feromonios(feromonios, taxa_evaporacao)
        for n in range(len(formigas)):
            log[f"geração{gen}"][n] = (formigas[n], distancias[n]) 
            adicionar_feromonios(formigas[n], distancias[n], Constante_feromonios, feromonios)
            if distancias[n] < melhor_distancia:
                melhor_rota, melhor_distancia = formigas[n], distancias[n]
    
    return melhor_distancia, melhor_rota, log


def plotar_caminho(caminho, distancia):
    data = abrir_arquivo(r"flyfoood\berlin52.csv")
    plt.title(str(distancia))
    for x,y in data:
        plt.scatter(x,y, c="black", s=16)
    for i in range(len(caminho)):
        plt.plot([data[caminho[i]][0], data[caminho[i-1]][0]], [data[caminho[i]][1], data[caminho[i-1]][1]], c = "black")
    plt.show()


if __name__ == "__main__":
    Constante_feromonios = 5
    Constante_proximidade = 300
    alfa = 2
    beta = 2
    taxa_evaporacao = 0.7
    feromonios_iniciais = 0.5
    qnt_geracoes = 100
    distancia, melhor, log = colonia(mapa, Constante_feromonios, Constante_proximidade, alfa, beta, taxa_evaporacao, feromonios_iniciais, qnt_geracoes)
    plotar_caminho(melhor, distancia)
