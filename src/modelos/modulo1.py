# pylint: disable=no-name-in-module
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers # pylint: disable=no-name-in-module
import matplotlib.pyplot as plt

consumo = np.array([[100], [200], [300], [400], [500], [600], [700], [800], [900], [1000]], dtype=float)
necesidad = np.array([
    [50, 20, 20, 10],
    [70, 60, 30, 40],
    [100, 100, 50, 50],
    [160, 120, 80, 40],
    [150, 200, 80, 70],
    [260, 140, 120, 80],
    [250, 200, 140, 110],
    [320, 240, 160, 80],
    [300, 300, 180, 120],
    [350, 250, 200, 200]
], dtype=float)

modelo = keras.Sequential([
    keras.Input(shape=(1,)),              # entrada: consumo total
    layers.Dense(64, activation="relu"),  # capa 1
    layers.Dense(128, activation="relu"), # capa 2
    layers.Dense(64, activation="relu"),  # capa 3
    layers.Dense(32, activation="relu"),  # capa 4
    layers.Dense(4)                       # salida: 4 casas
])

modelo.compile(optimizer="adam", loss="mse", metrics=["mae"])

print("Entrenando....")
historial = modelo.fit(consumo, necesidad, epochs=500, verbose=0)
print("ya entrenado")

# Gráfico de la pérdida
plt.figure(figsize=(8, 4))
plt.title("Evolución de la pérdida durante el entrenamiento")
plt.xlabel("# vuelta")
plt.ylabel("Mag de pérdida")
plt.plot(historial.history["loss"])
plt.grid(True)
plt.show()

def mostrar_regresion(modelo, consumo, necesidad):
    """Grafica las curvas de regresión aprendidas por el modelo."""
    x_vals = np.linspace(consumo.min(), consumo.max(), 100).reshape(-1, 1)
    predicciones = modelo.predict(x_vals)

    etiquetas = ["Casa A", "Casa B", "Casa C", "Casa D"]
    plt.figure(figsize=(8, 5))
    for i in range(4):
        plt.scatter(consumo, necesidad[:, i], label=f"Datos reales {etiquetas[i]}", alpha=0.6)
        plt.plot(x_vals, predicciones[:, i], label=f"Modelo {etiquetas[i]}")
    
    plt.title("Función de regresión del modelo predictivo")
    plt.xlabel("Consumo total (kWh)")
    plt.ylabel("Necesidad estimada (kWh)")
    plt.legend()
    plt.grid(True)
    plt.show()

mostrar_regresion(modelo, consumo, necesidad)

print("hacemos una prediccion")
ejemplo = np.array([[600]])
prediccion = modelo.predict(ejemplo)
print("A: {:.1f} kW, B: {:.1f} kW, C: {:.1f} kW, D: {:.1f} kW".format(*prediccion[0]))