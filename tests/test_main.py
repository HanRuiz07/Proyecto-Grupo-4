import numpy as np
import pytest
from src.modulo1 import modelo  # Importamos el modelo entrenado

def test_prediccion_valores_aproximados():
    entrada = np.array([[600.0]])
    salida_esperada = np.array([217, 176, 118, 90])
    salida_predicha = modelo.predict(entrada)[0]

    # Comprobamos que los valores predichos estén cerca de los esperados
    np.testing.assert_allclose(
        salida_predicha, salida_esperada, rtol=0.15,
        err_msg=f"Predicción fuera del rango esperado: {salida_predicha}"
    )

def test_dimensiones_salida():
    entrada = np.array([[500.0]])
    salida_predicha = modelo.predict(entrada)
    assert salida_predicha.shape == (1, 4), \
        f"Forma de salida inesperada: {salida_predicha.shape}"
