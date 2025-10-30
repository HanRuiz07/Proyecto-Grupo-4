class MLpredicator:
    """"
    Atributos:
    LinearRegression modelo
    bool entrenado
    float error_actual
    float umbral_error
    """

    #metodos
    def cargar_modelo():
        # importar pesos o configuracion previamente entrenada
        ...
    
    def entrenar_modelo_inicial(datos):
        #entrenamiento con el primer conjunto de datos historicos
        ...
    
    def predecir_sgte_hora(datos):
        #predecir el valor de SoC o carga esperada a corto plazo
        ...
    
    def verificar_desviacion():
        #evalua si la prediccion se mantiene en el rango aceptable
        ...