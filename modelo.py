import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import os


def entrenar_modelo(ruta_dataset, ruta_modelo):
    # Paso 1: Cargar el dataset
    dataset = pd.read_csv(ruta_dataset)

    # Paso 2: Separar características (X) y etiquetas (y)
    x = dataset.drop(columns=["ascensor_sel"])
    y = dataset["ascensor_sel"] - 1  # Los valores de los ascensores deben cambiar a 0 y 1 ya que solo permite binarios

    # Paso 3: Dividir en conjunto de entrenamiento y prueba
    # Se asignan las variables "x" e "y" donde se alojan los datos de entrada y las salidas esperadas, además, se
    # define 0.2 para que sea 20% de datos para pruebas y el resto (8%) para entrenar, el valor de random state es
    # usado para definir la division de datos que se usaran en el entrenamiento y el test
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    # Paso 4: Normalizar los datos de manera estándar, tanto para los datos de entrenamiento como de testing
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Paso 5: Construir el modelo
    # Crea la red neuronal con dos capas ocultas de 16 y 12 neuronas y una capa de salida para clasificación binaria,
    # donde 0 es el asc_1 y 1 es el asc_2, la activación relu se usa para las capas internas y Sigmoid para la salida
    model = Sequential([
        Dense(16, activation='relu', input_shape=(X_train.shape[1],)),
        Dense(12, activation='relu'),
        Dense(1, activation='sigmoid')  # Salida binaria (ascensor 1 o 2)
    ])

    # Paso 6: Compilar el modelo
    # Optimizador Adam, un algoritmo eficiente que ajusta automáticamente la tasa de aprendizaje para minimizar la
    # función de pérdida. Mide la diferencia entre la predicción del modelo (probabilidad entre 0 y 1) y la etiqueta
    # real (0 o 1). El modelo intentará minimizar esta pérdida. Además de minimizar la pérdida, durante el
    # entrenamiento calculará la precisión (accuracy) para mostrar qué tan bien está clasificando.
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Paso 7: Entrenar el modelo
    # model.fit es el método que entrena la red neuronal, se entrega los datos de entrada normalizados, las etiquetas
    # correctas que el modelo debe aprender a predecir, reserva el 20% de datos de entrenamiento para validación
    # (aparte de los datos de prueba), el epoch indica que el modelo recorrerá el conjunto de entrenamiento 50 veces,
    # batch size divide en grupos de 32 muestras para actualizar los pesos del modelo de forma incremental y verbose 1
    # muestra en consola el progreso del entrenamiento
    history = model.fit(X_train_scaled, y_train, validation_split=0.2, epochs=50, batch_size=32, verbose=1)

    # Paso 8: Evaluar el modelo
    # Evalúa el rendimiento del modelo usando los datos de prueba de entrada y salida, verbose 0 indica que no muestre
    # nada por consola
    loss, accuracy = model.evaluate(X_test_scaled, y_test, verbose=0)
    print(f"Precisión en test: {accuracy:.4f}")

    # Paso 9: Guardar el modelo
    os.makedirs("modelo", exist_ok=True)
    model.save(ruta_modelo)
    print(f"Modelo guardado.")
