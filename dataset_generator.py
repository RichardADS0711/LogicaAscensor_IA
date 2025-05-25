import numpy as np
import pandas as pd
import os

def calcular_destinos_pendientes(piso_actual, direccion_actual, num_pisos):
    if direccion_actual == 1:  # subiendo
        max_destinos = num_pisos - piso_actual - 1  # no puede pasarse del último piso
        return np.random.randint(1, max_destinos + 1) if max_destinos > 0 else 0
    elif direccion_actual == -1:  # bajando
        max_destinos = piso_actual  # no puede ir por debajo de 0
        return np.random.randint(1, max_destinos + 1) if max_destinos > 0 else 0
    else:  # detenido
        return 0

def estimar_tiempo(piso_actual, direccion_actual, piso_llamada, destinos_pendientes, direccion_llamada, vel_traslado):
    penalizacion_destinos = 2  # segundos extra por cada destino pendiente
    if direccion_actual != 0 and direccion_actual != direccion_llamada:
        penalizacion_direccion = 50  # alta penalización si va en sentido opuesto
    else:
        penalizacion_direccion = 0

    if direccion_actual == 1:
        if piso_actual > piso_llamada:
            penalizacion_posicion = 50
        else:
            penalizacion_posicion = 0
    elif direccion_actual == -1:
        if piso_actual < piso_llamada:
            penalizacion_posicion = 50
        else:
            penalizacion_posicion = 0
    else:
        penalizacion_posicion = 0

    tiempo_base = abs(piso_llamada - piso_actual) * vel_traslado
    tiempo_destinos = destinos_pendientes * penalizacion_destinos

    return tiempo_base + tiempo_destinos + penalizacion_direccion + penalizacion_posicion

def generar_datos(num_pisos, num_muestras, vel_traslado):
    data = []

    for _ in range(num_muestras):
        piso_llamada = np.random.randint(1, num_pisos)
        direccion_llamada = np.random.choice([-1, 1])  # 0: bajar, 1: subir

        piso_actual_asc_1 = np.random.randint(1, num_pisos)
        piso_actual_asc_2 = np.random.randint(1, num_pisos)

        direccion_actual_asc_1 = np.random.choice([-1, 0, 1])  # -1: baja, 0: detenido, 1: sube
        direccion_actual_asc_2 = np.random.choice([-1, 0, 1])

        destinos_pendientes_asc_1 = calcular_destinos_pendientes(piso_actual_asc_1, direccion_actual_asc_1, num_pisos)
        destinos_pendientes_asc_2 = calcular_destinos_pendientes(piso_actual_asc_2, direccion_actual_asc_2, num_pisos)

        personas_dentro_asc_1 = 1 if destinos_pendientes_asc_1 != 0 else 0
        personas_dentro_asc_2 = 1 if destinos_pendientes_asc_2 != 0 else 0

        tiempo_estimado_1 = estimar_tiempo(piso_actual_asc_1, direccion_actual_asc_1, piso_llamada,
                                           destinos_pendientes_asc_1, direccion_llamada, vel_traslado)
        tiempo_estimado_2 = estimar_tiempo(piso_actual_asc_2, direccion_actual_asc_2, piso_llamada,
                                           destinos_pendientes_asc_2, direccion_llamada, vel_traslado)

        if tiempo_estimado_1 <= tiempo_estimado_2:
            ascensor_sel = 1
        else:
            ascensor_sel = 2

        fila = [
            piso_llamada,
            direccion_llamada,
            piso_actual_asc_1,
            piso_actual_asc_2,
            direccion_actual_asc_1,
            direccion_actual_asc_2,
            destinos_pendientes_asc_1,
            destinos_pendientes_asc_2,
            personas_dentro_asc_1,
            personas_dentro_asc_2,
            tiempo_estimado_1,
            tiempo_estimado_2,
            ascensor_sel,
            num_pisos
        ]

        data.append(fila)

    columnas = [
        'piso_llamada',
        'direccion_llamada',
        'piso_actual_asc_1',
        'piso_actual_asc_2',
        'direccion_actual_asc_1',
        'direccion_actual_asc_2',
        'destinos_pendientes_asc_1',
        'destinos_pendientes_asc_2',
        'personas_dentro_asc_1',
        'personas_dentro_asc_2',
        'tiempo_traslado_asc_1',
        'tiempo_traslado_asc_2',
        'ascensor_sel',
        'cant_pisos'
    ]

    df = pd.DataFrame(data, columns=columnas)
    return df



def guardar_dataset(num_pisos, num_muestras, vel_traslado, nombre="dataset/dataset_ascensores.csv"):
    os.makedirs("dataset", exist_ok=True)
    df = generar_datos(num_pisos, num_muestras, vel_traslado)
    df.to_csv(nombre, index=False)
    print(f"Dataset generado y guardado como {nombre}")
