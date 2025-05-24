import os
from dataset_generator import guardar_dataset
from modelo import entrenar_modelo
from interfaz import iniciar_ui


# Variables de entorno
EST_SISTEMA = int(os.getenv("EST_SISTEMA", 1))
NUM_PISOS = int(os.getenv("NUM_PISOS", 10))
NUM_MUESTRAS = int(os.getenv("NUM_MUESTRAS", 750))
VEL_TRASLADO = int(os.getenv("VEL_TRASLADO", 3))
DATASET_PATH = "dataset/dataset_ascensores.csv"
MODEL_PATH = "modelo/modelo_ascensores.h5"

if __name__ == "__main__":
    print(f"Configuración:")
    print(f"-NUM_PISOS = {NUM_PISOS}")
    print(f"-NUM_MUESTRAS = {NUM_MUESTRAS}")
    print(f"-VEL_TRASLADO = {VEL_TRASLADO}")

    if os.path.exists(DATASET_PATH):
        print(f"El dataset ya existe. No se generará uno nuevo.")
    else:
        print(f"Generando Dataset...")
        guardar_dataset(
            num_pisos=NUM_PISOS,
            num_muestras=NUM_MUESTRAS,
            vel_traslado=VEL_TRASLADO,
            nombre=DATASET_PATH
        )

    if os.path.exists(MODEL_PATH):
        print(f"El modelo ya existe. No se entrenará uno nuevo.")
    else:
        print(f"Entrenando Modelo...")
        entrenar_modelo(ruta_dataset=DATASET_PATH, ruta_modelo=MODEL_PATH)

    print(f"Iniciando interfaz gráfica...")
    iniciar_ui(
        modelo_path=MODEL_PATH,
        num_pisos=NUM_PISOS,
        vel_traslado=VEL_TRASLADO,
        est_sistema=EST_SISTEMA
    )
