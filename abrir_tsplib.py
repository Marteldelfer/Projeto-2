import os, csv

def e_numero(x : str) -> bool:
    try:
        float(x)
        return True
    except:
        return False
def main():
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

if __name__ == "__main__":
    main()