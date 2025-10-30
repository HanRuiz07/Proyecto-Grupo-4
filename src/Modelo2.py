import numpy as np
from keras.layers import Dense
from keras.models import Sequential
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from joblib import dump

dataset = np.loadtxt("../Data/libro1.csv", delimiter=',')

Tiempo = dataset[:, 1]
I = dataset[:, 0]

I_prev = np.zeros_like(I)
I_prev[2:] = I[:-2]
I_prev[0:2] = I[0]

I_post = np.zeros_like(I)
I_post[-2:] = np.nan
I_post[-2:] = I[:2]

I_prev4 = np.zeros_like(I)
I_prev4[4:] = I[:-4]
I_prev4[0:4] = I[0]

I_post4 = np.zeros_like(I)
I_post4[-4:] = np.nan
I_post4[-4:] = I[:4]

Entrada = np.column_stack((I, I_prev, I_prev4, I_post4, I_post,Tiempo))
Salida = dataset[:, 2]

scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

Entrada_norm = scaler_X.fit_transform(Entrada)
Salida_norm = scaler_y.fit_transform(Salida.reshape(-1, 1))

dump(scaler_X, 'scaler_X.save')
dump(scaler_y, 'scaler_y.save')

model = Sequential()
model.add(Dense(32, input_dim = 6, activation ='relu')) 
model.add(Dense(16, activation='relu')) 
model.add(Dense(8, activation= 'relu'))
model.add(Dense(1, activation= 'linear'))

model.compile(loss='mse', optimizer='adam', metrics=['mae'])

historial = model.fit(Entrada_norm, Salida_norm, epochs=200, batch_size=16, verbose=1)

predicciones_norm = model.predict(Entrada_norm)
predicciones = scaler_y.inverse_transform(predicciones_norm)

plt.figure(figsize=(8, 5))
plt.plot(historial.history['loss'], label='Pérdida (MSE)')
plt.title("Funcion de pérdida")
plt.xlabel("Época")
plt.ylabel("MSE")
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(9, 5))
plt.scatter(Tiempo, Salida, color='blue', label='Datos reales', alpha=0.7)
plt.scatter(Tiempo, predicciones, color='red', label='Predicciones del modelo', alpha=0.7)
plt.title("Valores reales vs valores predichos")
plt.xlabel("Minutos")
plt.ylabel("Tiempo hasta el próximo pico")
plt.legend()
plt.grid(True)
plt.show()

model.save("Modelo_entrenado.keras")