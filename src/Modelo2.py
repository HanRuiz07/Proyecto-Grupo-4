import numpy as np
from keras.layers import Dense
from keras.models import Sequential
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

dataset = np.loadtxt("../Data/libro1.csv", delimiter=',')

I = dataset[:, 0]
I_prev = np.zeros_like(I)
I_prev[2:] = I[:-2]
I_prev[0:2] = I[0]

Tiempo = dataset[:, 1]

Entrada = np.column_stack((I, I_prev,Tiempo))
Salida = dataset[:, 2]

#normalización del modelo
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

Entrada_norm = scaler_X.fit_transform(Entrada)
Salida_norm = scaler_y.fit_transform(Salida.reshape(-1, 1))


model = Sequential()
model.add(Dense(32, input_dim = 3, activation ='relu')) 
model.add(Dense(16, activation='relu')) 
model.add(Dense(1, activation= 'linear'))

model.compile(loss='mse', optimizer='adam', metrics=['mae'])

historial = model.fit(Entrada_norm, Salida_norm, epochs=200, batch_size=16, verbose=1)

predicciones_norm = model.predict(Entrada_norm)
predicciones = scaler_y.inverse_transform(predicciones_norm)

plt.figure(figsize=(8, 5))
plt.plot(historial.history['loss'], label='Pérdida (MSE)')
plt.title("Evolución de la función de pérdida durante el entrenamiento")
plt.xlabel("Época")
plt.ylabel("Pérdida (MSE)")
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(9, 5))
plt.scatter(Tiempo, Salida, color='blue', label='Datos reales', alpha=0.7)
plt.scatter(Tiempo, predicciones, color='red', label='Predicciones del modelo', alpha=0.7)
plt.title("Comparación entre valores reales y predichos")
plt.xlabel("Tiempo (minutos)")
plt.ylabel("Tiempo hasta el próximo pico")
plt.legend()
plt.grid(True)
plt.show()

model.save("Modelo_entrenado.keras")