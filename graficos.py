import matplotlib.pyplot as plt
import math

eixoX = [i for i in range(1, 200)]

log = [math.log2(i) for i in eixoX]
sqrN = [math.sqrt(i) for i in eixoX]
n = [i for i in eixoX]
nlog = [i * math.log2(i) for i in eixoX]
nSqr = [i ** 2 for i in eixoX]
nCub = [i ** 3 for i in eixoX]
twoN = [2 ** i for i in eixoX]
nN = [i ** i for i in eixoX]
nFat = [math.factorial(int(i)) for i in eixoX if i < 100] + [100000 for _ in range(100)]

plt.ylim(top=200)
plt.plot(eixoX, [1 for _ in eixoX], label='1')
plt.plot(eixoX, log, label='log(n)')
plt.plot(eixoX, sqrN, label='sqr(n)')
plt.plot(eixoX, n, label='n')
plt.plot(eixoX, nlog, label='n log(n)')
plt.plot(eixoX, nSqr, label='n ** 2')
plt.plot(eixoX, twoN, label='2 ** n')
plt.plot(eixoX, nFat, label='fat(n)')
plt.legend()
plt.show()