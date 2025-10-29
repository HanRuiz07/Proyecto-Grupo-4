import numpy as np
from keras.layers import Dense
from keras.models import Sequential

dataset = np.loadtxt("../Data/libro1.csv", delimiter=',')
D1 = dataset [:, 0]
D2 = dataset [:, 1]
D3 = dataset [:, 2]
D4 = dataset [:, 3]

print(dataset)
print("D1:", D1)
print("D2:", D2)
print("D3:", D3)
print("D4:", D4)