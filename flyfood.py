arquivo_entrada = 'mapa.txt'

def abrir_mapa(mapa_arquivo:str): # retorna um dicionário com as coordenadas de cada ponto de interesse no mapa
    # essas coordenadas são contadas começando do 0, da esquerda para a direita no x e de cima para baixo no y
    matriz_entrada = {}
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
                matriz_entrada[i] = (y,x)
            x += 1

    return matriz_entrada


def distancia(a,b,matriz): # encontra a distancia entre 2 casas
    distancia_y = abs(matriz[a][0] - matriz[b][0])
    distancia_x = abs(matriz[a][1] - matriz[b][1])
    return (distancia_x ** 2 + distancia_y ** 2) ** 0.5 # Distância euclideana


def permutar(lista, passo = 0):

    if passo == len(lista): # Caso base
        yield lista # Salva uma cópia da lista se tiver terminado as permutações
    else:
        for index in range(passo, len(lista)): 

            lista[passo], lista[index] = lista[index], lista[passo]
            yield from permutar(lista, passo + 1)
            lista[passo], lista[index] = lista[index], lista[passo] # Restaura estado da linha para evitar repetição 


def forca_bruta(matriz):
    casas = list(matriz)
    casas.remove('R')

    permutacoes = permutar(casas)

    caminho_menor, tamanho_menor = (), float('inf')
    for caminho in permutacoes:
        tamanho = 0
        casa_anterior = 'R' #começa pelo R
        for casa in caminho:
            tamanho += distancia(casa, casa_anterior, matriz)
            casa_anterior = casa
            if tamanho > tamanho_menor: # para o loop caso o tamanho seja maior que o esperado
                break

        else: # retorna ao inicio e confere se é o menor
            tamanho += distancia(casa_anterior, 'R', matriz)
            if tamanho < tamanho_menor:
                caminho_menor = caminho
                tamanho_menor = tamanho

    return caminho_menor, tamanho_menor # Adicionando à solução, retornamos a distância percorrida



matriz_de_entrada = abrir_mapa(arquivo_entrada)
caminho, tamanho = forca_bruta(matriz_de_entrada)
for casa in caminho:
    print(casa, end=' ')
print()
print('distância percorrida: %.2fdm (dronômetros)' % tamanho)
