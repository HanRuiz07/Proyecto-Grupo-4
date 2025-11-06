import os

import numpy as np
from keras.layers import Dense
from keras.models import Sequential
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from joblib import dump
import streamlit as st
from keras.models import load_model # pylint: disable=import-error
from joblib import load

print("Directorio actual:", os.getcwd())


def cargar_datos(csv):
    """
    Función para guardar los datos con los que se va a trabajar en un archivo csv
    """
    try:
        print("Datos cargados exitosamente")
        return np.loadtxt(csv, delimiter=',')
    except FileNotFoundError:
        print("Error al cargar el archivo")

#dataset = np.loadtxt("Data/libro1.csv", delimiter=',')

#Tiempo = dataset[:, 1]
#I = dataset[:, 0]

#I_prev = np.zeros_like(I)
#I_prev[2:] = I[:-2]
#I_prev[0:2] = I[0]

#I_post = np.zeros_like(I)
#I_post[-2:] = np.nan
#I_post[-2:] = I[:2]

#I_prev4 = np.zeros_like(I)
#I_prev4[4:] = I[:-4]
#I_prev4[0:4] = I[0]

#I_post4 = np.zeros_like(I)
#I_post4[-4:] = np.nan
#I_post4[-4:] = I[:4]

def entrenar_modelo(datos):
    """
    Se define 4 valores de corriente extra y se entrena el modelo con 6 entradas
    """
    tiempo = datos[:, 1]
    i = datos[:, 0]

    i_prev = np.zeros_like(i)
    i_prev[2:] = i[:-2]
    i_prev[0:2] = i[0]

    i_post = np.zeros_like(i)
    i_post[-2:] = np.nan
    i_post[-2:] = i[:2]

    i_prev4 = np.zeros_like(i)
    i_prev4[4:] = i[:-4]
    i_prev4[0:4] = i[0]

    i_post4 = np.zeros_like(i)
    i_post4[-4:] = np.nan
    i_post4[-4:] = i[:4]

    entrada = np.column_stack((i, i_prev, i_prev4, i_post4, i_post,tiempo))
    salida = datos[:, 2]

    scaler_x = MinMaxScaler()
    scaler_y = MinMaxScaler()

    entrada_norm = scaler_x.fit_transform(entrada)
    salida_norm = scaler_y.fit_transform(salida.reshape(-1, 1))

    model = Sequential()
    model.add(Dense(32, input_dim = 6, activation ='relu'))
    model.add(Dense(16, activation='relu'))
    model.add(Dense(8, activation= 'relu'))
    model.add(Dense(1, activation= 'linear'))

    model.compile(loss='mse', optimizer='adam', metrics=['mae'])

    historial = model.fit(entrada_norm, salida_norm, epochs=200, batch_size=16, verbose=1)

    predicciones_norm = model.predict(entrada_norm)
    predicciones = scaler_y.inverse_transform(predicciones_norm)

    st.subheader("Función de pérdida")
    fig1, ax1 = plt.subplots(figsize=(8,4))
    ax1.plot(historial.history['loss'], label='MSE')
    ax1.set_xlabel("Épocas")
    ax1.set_ylabel("MSE")
    ax1.legend()
    ax1.grid(True)
    st.pyplot(fig1)

    st.subheader("Valores reales vs predicciones")
    fig2, ax2 = plt.subplots(figsize=(9,5))
    ax2.scatter(tiempo, salida, color='blue', label='Datos reales', alpha=0.7)
    ax2.scatter(tiempo, predicciones, color='red', label='Predicciones', alpha=0.7)
    ax2.set_xlabel("Tiempo")
    ax2.set_ylabel("Salida")
    ax2.legend()
    ax2.grid(True)
    st.pyplot(fig2)

    dump(scaler_x, 'scaler_X.save')
    dump(scaler_y, 'scaler_y.save')

    return model, scaler_x, scaler_y

def guardar_modelo(modelo):
    """Esta funcion guarda el modelo como un archivo keras para luego ser usado sin volver a entrenar el modelo"""
    modelo.save("Modelo_entrenado.keras")

def predecir(nuevos_valores):
    """Funcion que realiza una predicción con el modelo.keras la entrada a esta funcion debe ser un array"""
    modelo = load_model("Modelo_entrenado.keras")
    scaler_x = load("scaler_X.save")
    scaler_y = load("scaler_y.save")
    
    valores_norm =scaler_x.transform(nuevos_valores)
    prediccion_norm = modelo.predict(valores_norm)
    prediccion = scaler_y.inverse_transform(prediccion_norm)
    
    return prediccion