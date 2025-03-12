from flyfood_colonia import *
from flyfood_genetico import *
from flyfood_recozimento import *
from auxiliar import plotar_caminho
from typing import List, Tuple, Callable
import random, time, tqdm, math, matplotlib.pyplot as plt
from flyfood import forca_bruta
import pandas as pd
import imageio
from busca_aleatoria import ler_caminho
from os import listdir, remove
from os.path import isfile, join
from abrir_tsplib import e_numero
import seaborn

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
        remove(f"./figs/{arquivo}")
    
    algoritmo(plot=True)
    arquivos = [f for f in listdir("figs") if isfile(join("figs", f))]
    arquivos.sort(key=lambda a: int(a[-8:-4]))
    imagens = []
    for a in arquivos:
        imagens.append(imageio.v2.imread(f"./figs/{a}"))
    imageio.mimsave("gifs/gif.gif", imagens)

def genetico_teste(
        nome_arquivo : str = "mapas/berlin52.csv",
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
        plot : bool = False,
        cordenadas : List[Tuple[float, float]] = None
) -> Tuple:
    """
    O algoritmo propriamente dito. Retorna a menor distancia, o menor caminho e um 
    registro de cada geração.
    
    Itera `n_geracoes` vezes, atualizando feromônios a cada geração
    """

    comeco = time.process_time_ns()
    tempo *= 10**9

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
        t.set_description(f"Melhor distância : {melhor_distancia}")
    
        if tempo < time.process_time_ns() - comeco:
            break
        if plot:
            plotar_caminho(
                caminho=melhor_rota,
                dist=melhor_distancia, 
                plotar=False,
                salvar=True, 
                nome_fig=f"colônia_{gen:04d}", 
                titulo="Colônia de Formigas",
            )

            """entrada = [(x, y) for x in range(52) for y in range(52) if x != y]
            a = [encontrar_na_tabela(i, j, feromonios) * 3 for i in range(52) for j in range(52) if i != j]
            for ine, e in enumerate(entrada):
                plt.plot([cordenadas[e[0]][0], cordenadas[e[1]][0]], [cordenadas[e[0]][1], cordenadas[e[1]][1]], c='red', 
                         alpha = a[ine], label='_no_legend')
            plt.title("Evolução dos feromônios")
            plt.savefig(f"./figs/colônia_{gen:04d}")
            plt.clf()"""
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
                            titulo="Recozimento Simulado",)
        counter += 1
        if tempo < time.process_time_ns() - comeco:
            break

        temperatura *= resfriamento
        t.set_description(f"Temperatura : {(temperatura - temp_minima):.5f} | Distânciaa : {melhor_distancia:.5f}")
    t.close()
    return melhor_caminho, melhor_distancia

def tamanho_grafo(nome : str) -> int:
    nome = nome[:-4]
    res = ""
    for letra in nome[::-1]:
        if not e_numero(letra):
            break
        res += letra
    return int(res[::-1])


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

    """x = ["Algoritmo Genético", "Recozimento Simulado", "Colônia de Formigas"]

    res = []
    t = 1
    res.append(sum(genetico_teste(tempo=t)[0] for _ in range(10)) / 10)
    res.append(sum(otimizar_rota_teste(tempo=t)[1] for _ in range(10)) / 10)
    res.append(sum(colonia_teste(n_geracoes=100000, tempo=t)[0] for _ in range(10)) / 10)

    plt.ylim(0, 15000)
    plt.title(f"Distância encontrada em {t} segundo")
    plt.ylabel("Distância")
    plt.bar(x, res)
    plt.show()"""
    
    for a in listdir("mapas"):
        if tamanho_grafo(a) < 300:
            continue
        print(a)
    a = "a280.csv"
    cordenadas = abrir_arquivo(f"mapas/{a}")
    grafo = gerar_grafo(f"mapas/{a}")
    for i, x in enumerate(cordenadas):
        for j, y in enumerate(cordenadas):
            if i == j:
                continue
            if x == y:
                print(i, j, x)
        
    print(a)
    colonia(grafo)
    genetico(grafo)
    otimizar_rota(localizacoes=cordenadas, temp_minima=1)
    """ 
    res_col = []
    for _ in range(15):
        teste = colonia(n_geracoes=25 ,mapa=gerar_grafo("mapas/ch150.csv"))[0]
        res_col.append(teste)

    res_rec = []
    for _ in range(15):
        teste = otimizar_rota(temp_minima=1, localizacoes=abrir_arquivo("mapas/ch150.csv"))[0]
        res_rec.append(teste)

    res_gen = []
    for _ in range(15):
        teste = genetico(mapa=gerar_grafo("mapas/ch150.csv"),n_populacao=120, tempo=15)[0]
        res_gen.append(teste)

    print(res_gen, res_col, res_rec) 
    """
    """ 
    #berlin52
    res_gen, res_col , res_rec = ([9135.190029438318, 9151.226342675025, 9145.99736271883, 8802.447329482551, 8939.955168062574, 
                                  9271.976646664687, 9194.982121138413, 9526.960907175164, 8791.772181864431, 8691.048810189515, 
                                  8872.194718890458, 9510.749706795214, 8903.32837622082, 9145.500607877022, 9617.667430351481], 
                                [7709.006604456741, 7840.469823582665, 7845.096631702759, 7576.545658228342, 7978.331698105634, 
                                 7760.819114527049, 7709.00660445674, 7962.297355583837, 7659.254629723315, 7681.749965600121, 
                                 7769.884342738844, 8013.0574624837955, 7832.766165608487, 7681.74996560012, 7766.663801883698], 
                                [8575.762752312266, 8472.579539660675, 8469.732525303356, 8253.225154365478, 7954.632751548155, 
                                 7834.082387097307, 8757.42834394611, 8159.230094273191, 8194.89685324503, 8342.422921327996, 
                                 8330.449450705468, 8267.387240923907, 8811.147991111813, 9018.852282004746, 8866.652898088892]) 
    """
    """
    #gr96
    res_gen, res_col , res_rec = ([856.757468963324, 1417.5187523889742, 1153.9487705679442, 1009.9439486803072, 1149.1706439381583, 
                                   1196.8945144761515, 1545.7685823718853, 992.5057568768987, 1047.2066884041647, 956.4281773168146, 
                                   883.8435762088412, 1443.9718907367032, 1085.773824720367, 937.4963580772921, 1293.8645459891509], 
                                   [558.601422168331, 571.4263526890732, 559.846762089491, 557.3615954519416, 542.6813687399756, 
                                    548.6598523802828, 555.6669612073642, 551.1451118134656, 568.749088882226, 539.9795186189249, 
                                    545.4671851222356, 560.330829529645, 563.4196803548595, 562.0055659759125, 550.6509989204759], 
                                    [643.8308270597241, 655.6823450301583, 634.7750165978729, 661.2943042832368, 676.9139651682027, 
                                     640.1954126348301, 664.7694981929981, 648.8686532199749, 669.9343245456045, 680.3023639349506, 
                                     665.2203756029955, 654.0843177867922, 689.1224911409134, 671.7325230075353, 687.4852587883103])
    """
    """ 
    #ch150
    res_gen, res_col , res_rec = ([39040.332381817636, 39795.50035206991, 39745.71600746623, 38665.29557261328, 39428.91707358956, 
                                   41452.73547715629, 40030.508703572545, 41326.715216253375, 40111.64791279337, 42174.22715469573, 
                                   40109.65040262366, 40199.513471672566, 42940.29507934958, 41804.613875681716, 38653.100277703015], 
                                   [7056.262852610913, 6959.394597649747, 6933.457710589571, 6892.460564836896, 6941.619604117921, 
                                    7076.123044653091, 6988.417967787642, 7043.616378235232, 6969.685893334197, 7031.622691465799, 
                                    6993.151364304481, 7052.981906292779, 7099.567687653899, 7056.606027839091, 6843.294039422823], 
                                    [8630.05105609581, 10188.650402269135, 9883.381364037816, 10095.157639410958, 9870.164323481227, 
                                     8884.992919564049, 9401.599866487639, 9770.555932648876, 9890.067405769263, 9593.741649318425, 
                                     9496.58677100801, 8505.58359880689, 9848.323523620094, 9608.297072180321, 10212.32104136042])
    
    menor = (distancia_caminho(grafo=gerar_grafo('mapas/ch150.csv'), caminho=ler_caminho('ch150.csv')))

    y = (list(map(lambda x: (x / menor - 1) * 100, res_gen)) + 
         list(map(lambda x: (x / menor - 1) * 100, res_rec)) +
         list(map(lambda x: (x / menor - 1) * 100, res_col)))
    x = ["Algoritmo genético"] * 15 + ["Recozimentos simulados"] * 15 + ["Colônia de formigas"] * 15
    df = {"Algoritmo" : x, "Porcentagem de perda sobre a solução ótima" : y}
    df = pd.DataFrame(df)
    """
    """ 
    seaborn.boxplot(df, x="Algoritmo", y="Porcentagem de perda sobre a solução ótima")
    plt.title("Comparação dos algoritmos pela entrada ch150")
    plt.show()
    plt.clf()
    """
    """ 
    plt.bar(["GA", "SA", "ACO"], 
            [(sum(res_gen) / 15 / menor - 1) * 100, (sum(res_rec) / 15 / menor - 1) * 100, (sum(res_col) / 15 / menor - 1) * 100],
            color=['red', 'orange', 'yellow'],
            label = ["Algoritmo genético", "Recozimentos simulados", "Colônia de formigas"])
    plt.title("Comparação dos algoritmos pela entrada ch150")
    plt.ylabel("Porcentagem de perda média sobre a solução ótima")
    plt.legend(loc=1)
    plt.show()
    """
    """ fb_x = list(range(4, 13))
    fb_y = [33934, 96367, 417461, 2451347, 19100217, 139646165, 1440179915, 14589651353, 165644493573]
    fb_y = [i / 10e9 for i in fb_y]

    cl_x = [gerar_coordenadas_aleatorias(i)[0] for i in range(4, 13)]
    cl_y = []
    for entrada in cl_x:
        comeco = time.process_time_ns()
        colonia(mapa=entrada, n_geracoes=50)
        cl_y.append(time.process_time_ns() - comeco)
    print(cl_y)
    cl_y = [i / 10e9 for i in cl_y]

    gn_x = [gerar_coordenadas_aleatorias(i)[0] for i in range(4, 13)]
    gn_y = []
    for entrada in gn_x:
        comeco = time.process_time_ns()
        genetico(mapa=entrada, n_geracoes=2000, tempo=15)
        gn_y.append(time.process_time_ns() - comeco)
    print(gn_y)
    gn_y = [i / 10e9 for i in gn_y]

    rc_x = [gerar_coordenadas_aleatorias(i)[1] for i in range(4, 13)]
    rc_y = []
    for entrada in rc_x:
        comeco = time.process_time_ns()
        otimizar_rota(localizacoes=entrada, temp_minima=10)
        rc_y.append(time.process_time_ns() - comeco)
    print(rc_y)
    rc_y = [i / 10e9 for i in rc_y]

    print(list(zip(gn_y, cl_y, rc_y, fb_y))) """

    """ i  = 8

    total = [(0.111326075, 0.0007370002, 0.2335902734, 3.3934e-06), (0.1062765788, 0.0005735736, 0.2527558339, 9.6367e-06), (0.1210193611, 0.0009732848, 0.276968208, 4.17461e-05), (0.1296505835, 0.0015128204, 0.3061958436, 0.0002451347), (0.1399619288, 0.0020993322, 0.3194418399, 0.0019100217), (0.1489020721, 0.0030285137, 0.3484741007, 0.0139646165), (0.1583491347, 0.0039865957, 0.3746372575, 0.1440179915), (0.1658972119, 0.0046748392, 0.3826761169, 1.4589651353), (0.1733868016, 0.0052065947, 0.4214437929, 16.5644493573)]
    gn_y, rc_y, cl_y, fb_y = [], [], [], []
    for a, b, c, d in total:
        gn_y.append(a * 10)
        cl_y.append(b * 10)
        rc_y.append(c * 10)
        fb_y.append(d * 10)

    plt.bar(["GA", "SA", "ACO", "BF"], 
            [gn_y[i], rc_y[i], cl_y[i], fb_y[i]], 
            color = ['red', 'orange', 'yellow', 'green'],
            label=['Algoritmo genético', 'Recozimento simulado', 'Colônia de formigas', 'Força bruta'])
    plt.legend(loc=1)
    plt.ylabel("Tempo em segundos")
    plt.xlabel("Algoritmos")
    plt.title(f"Comparação do tempo de execução dos algoritmos para {i + 4} pontos")
    plt.show()
     """

    def mapa_aleatorio(cordenadas):
        #Transforma de lista para dict
        res = dict()
        for c in range(len(cordenadas)):
            res[str(c) if c != len(cordenadas) - 1 else 'R'] = cordenadas[c]
        return res

    """ x = [gerar_coordenadas_aleatorias(pontos=i) for i in [8, 10, 12]]
    fb_x = [mapa_aleatorio(xi[1]) for xi in x]

    print(fb_x[0])

    gn_y = [sum(genetico(mapa=xi[0], tempo=15)[0] for _ in range(20)) / 20 for xi in x]
    cl_y = [sum(colonia(mapa=xi[0])[0] for _ in range(20)) / 20 for xi in x]
    rc_y = [sum(otimizar_rota(localizacoes=xi[1], temp_minima=10)[0] for _ in range(20)) / 20 for xi in x]
    fb_y = [forca_bruta(xi)[1] for xi in fb_x]

    print(fb_y, gn_y, cl_y, gn_y)

    gn_y = [(g / f - 1) * 100 for g, f in zip(gn_y, fb_y)]
    rc_y = [(g / f - 1) * 100 for g, f in zip(rc_y, fb_y)]
    cl_y = [(g / f - 1) * 100 for g, f in zip(cl_y, fb_y)]
    """
    """ 
    for i in range(3):

        plt.bar(["GA", "SA", "ACO"], 
                [], 
                color=['red', 'orange', 'yellow'],
                label=['Algoritmo genético', 'Recozimento simulado', 'Colônia de formigas'])
        plt.legend(loc=1)
        plt.ylabel("Perda em porcentagem")
        plt.ylim(bottom=0)
        plt.xlabel("Algoritmos")
        plt.title(f"Comparação da perda em relação à solução ótima dos algoritmos para {i*2 + 8} pontos")
        plt.show()
        """

    p = '../../feromonios'
    arquivos = [f for f in listdir("../../feromonios")]
    arquivos.sort(key=lambda a: int(a[-8:-4]))
    imagens = []
    for a in arquivos:
        imagens.append(imageio.v2.imread(f"../../feromonios/{a}"))
    imageio.mimsave("gifs/gif.gif", imagens)
