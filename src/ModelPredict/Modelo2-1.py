import numpy as np
from tensorflow.keras.models import load_model
from joblib import load

# 1️⃣ Cargar modelo y scalers guardados
model = load_model("Modelo_entrenado.keras")
scaler_X = load('scaler_X.save')
scaler_y = load('scaler_y.save')

# 2️⃣ Definir entrada de prueba
# Columnas: I, I_prev, I_prev4, I_post4, I_post, Tiempo
entrada = np.array([[9.8, 15.6, 40, 10.5, 11, 100],
                    [10.8, 20, 37, 10.2, 9.5, 122]])

# 3️⃣ Normalizar entrada usando el scaler del entrenamiento
entrada_norm = scaler_X.transform(entrada)

# 4️⃣ Hacer predicción
prediccion_norm = model.predict(entrada_norm)

# 5️⃣ Desnormalizar la salida para obtener valores reales
prediccion = scaler_y.inverse_transform(prediccion_norm)

print("Predicción del modelo:")
print(prediccion)
