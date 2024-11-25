arquivo_entrada = 'mapa.txt'

def abrir_mapa(mapa_arquivo:str): # retorna um dicionário com as coordenadas de cada ponto de interesse no mapa.
    # essas coordenadas são contadas começando do 0.
    matriz_mapa = {}
    y, x = 0, 0 # armazena as coordenadas que estão sendo lidas em cada loop.
    with open(mapa_arquivo, 'r') as arquivo_de_entrada:
        mapa = arquivo_de_entrada.read()
        len_y, len_x = 0, 0
        for i in mapa:

            if i == ' ' or i == '\n': # ignora os espaços e quebras de linha
                continue

            if len_x == 0: # para verificar os dois primeiros números
                if len_y == 0: # coloca o primeiro número como tamanho Y
                    len_y = int(i)
                else: # coloca o segundo número como tamanho X
                    len_x = int(i)
                continue

            if x == len_x:
                x = 0
                y += 1

            if i != '0':
                matriz_mapa[i] = (y,x)
            x += 1
    print(matriz_mapa) # remover essa linha no código final
    return matriz_mapa


def get_distancia(a,b,matriz): # encontra a distancia entre 2 casas
    distancia_y = abs(matriz[a][0] - matriz[b][0])
    distancia_x = abs(matriz[a][1] - matriz[b][1])
    return (distancia_x ** 2 + distancia_y ** 2) ** 0.5 # Distância euclideana


def salvar(permutacoes, permutacao):
    permutacoes.append(permutacao)
    return permutacoes

def permutar(permutacoes, lista, passo = 0):

    if passo == len(lista): # Caso base
        salvar(permutacoes, lista[:]) # Salva uma cópia da lista se tiver terminado as permutações

    for index in range(passo, len(lista)): 

        lista[passo], lista[index] = lista[index], lista[passo]
        permutar(permutacoes, lista, passo + 1)

        lista[passo], lista[index] = lista[index], lista[passo] # Restaura estado da linha para evitar repetição 
    return permutacoes


def forca_bruta(matriz):
    casas = list(matriz)
    casas.remove('R')

    permutacoes = permutar([], casas)

    caminho_menor, tamanho_menor = (), float('inf')
    for caminho in permutacoes:
        tamanho = 0
        casa_anterior = 'R' #começa pelo R
        for casa in caminho:
            tamanho += get_distancia(casa, casa_anterior, matriz)
            casa_anterior = casa
            if tamanho > tamanho_menor: # para o loop caso o tamanho seja maior que o esperado.
                break

        else: # retorna ao inicio
            tamanho += get_distancia(casa_anterior, 'R', matriz)
            if tamanho < tamanho_menor:
                caminho_menor = caminho
                tamanho_menor = tamanho

    return caminho_menor, tamanho_menor # no código final, retorne apenas o caminho.



mapa = abrir_mapa(arquivo_entrada)
caminho, tamanho = forca_bruta(mapa)
for casa in caminho:
    print(casa, end=' ')
print()
print('distância percorrida: %.2fdm (dronômetros)' % tamanho)
