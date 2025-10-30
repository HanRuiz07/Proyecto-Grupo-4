import os
import numpy as np
import tensorflow as tf

# ------------------------------
# Cargar el modelo entrenado
# ------------------------------
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_modelo = os.path.join(ruta_actual, "modelo_entrenado.keras")

# Carga del modelo Keras
modelo = tf.keras.models.load_model(ruta_modelo)

# ------------------------------
# Función para predecir nuevos datos
# ------------------------------
def predecir(entrada):
    """
    Recibe una lista o numpy array con los valores de entrada,
    y devuelve la predicción del modelo entrenado.
    """
    entrada = np.array(entrada).reshape(1, -1)
    prediccion = modelo.predict(entrada)
    return float(prediccion[0][0]) if prediccion.shape == (1, 1) else prediccion.tolist()

# ------------------------------
# Prueba local (solo si se ejecuta directamente)
# ------------------------------
if __name__ == "__main__":
    ejemplo = [0.5, 0.7, 0.2]  # <-- cambia según tus features
    resultado = predecir(ejemplo)
    print("Predicción de prueba:", resultado)
