import os, csv, requests, tarfile, gzip, shutil

def e_numero(x : str) -> bool:
    try:
        float(x)
        return True
    except:
        return False
def main():

    response = requests.get("http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/ALL_tsp.tar.gz", stream=True)
    if response.status_code == 200:
        with open("ALL_tsp.tar.gz", "wb") as f:
            f.write(response.raw.read())

    if not os.path.exists("tsp_gz"):
        os.mkdir("tsp_gz")
    os.chdir("tsp_gz")

    with tarfile.open("../ALL_tsp.tar.gz", "r:gz") as tar:
        tar.extractall()

    os.chdir("..") 
    if not os.path.exists("tsplib"):
        os.mkdir("tsplib")

    for a in os.listdir("tsp_gz"):
        with gzip.open(f'tsp_gz/{a}', 'rb') as f_in:
            with open(f'tsplib/{a[:-3]}', 'wb') as f_out:
                f_out.write(f_in.read())

    if not os.path.exists("mapas"):
        os.mkdir("mapas")

    for a in os.listdir("tsplib"):
        if a[-3:] != "tsp":
            continue
        print(a)

        with open(f"tsplib/{a}", 'rb') as f:
            lista = []
            cordenadas = True

            for linha in f.readlines():
                if len(linha.split()) == 0:
                    continue
                if e_numero(linha.split()[0]):
                    if len(linha.split()) != 3:
                        cordenadas = False
                        break
                    lista.append([float(n) for n in linha.split()[1:]])

        if cordenadas:
            with open(f"mapas/{a[:-4]}.csv", "w", newline="") as f:
                csv.writer(f).writerows(lista)

    os.remove("ALL_tsp.tar.gz")
    shutil.rmtree("tsp_gz")
    
if __name__ == "__main__":
    main()
    print()
    for a in os.listdir("mapas"):
        print(tamanho_grafo(f"mapas/{a}"))