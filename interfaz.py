import tkinter as tk
from tkinter import messagebox
import numpy as np
from tensorflow.keras.models import load_model
import random


class Ascensor:
    def __init__(self, nombre, num_pisos):
        self.nombre = nombre
        self.num_pisos = num_pisos
        self.reset_estado()

    def reset_estado(self):
        self.piso_actual = random.randint(0, self.num_pisos - 1)
        if self.piso_actual == 0:
            self.direccion = random.choice(["subiendo", "detenido"])

        elif self.piso_actual == self.num_pisos-1:
            self.direccion = random.choice(["bajando", "detenido"])

        else:
            self.direccion = random.choice(["subiendo", "bajando", "detenido"])

        if self.direccion == "detenido":
            self.destinos = []

        elif self.direccion == "subiendo":
            pisos_superiores = [p for p in range(self.piso_actual + 1, self.num_pisos)]
            k = random.randint(1, min(5, len(pisos_superiores)))
            self.destinos = random.sample(pisos_superiores, k) if k > 0 else []

        elif self.direccion == "bajando":
            pisos_inferiores = [p for p in range(0, self.piso_actual)]
            k = random.randint(1, min(5, len(pisos_inferiores)))
            self.destinos = random.sample(pisos_inferiores, k) if k > 0 else []
        # Asegurar que el piso actual no esté en destinos pendientes
        if self.piso_actual in self.destinos:
            self.destinos.remove(self.piso_actual)
        self.destinos.sort()

        self.personas_dentro = 1 if self.destinos.__len__() > 0 else 0
        self.luces = 1 if self.personas_dentro == 1 else 0

    def actualizar_estado(self):
        return (
            f"Piso actual: {self.piso_actual + 1}\n"
            f"Dirección: {self.direccion}\n"            
            f"Luces: {'Encendidas' if self.luces == 1 else 'Apagadas'}\n"
            f"Personas Dentro: {'Sí' if self.personas_dentro == 1 else 'No'}\n"
            f"Destinos Pendientes: {[d+1 for d in self.destinos]}"
        )


class InterfazAscensores(tk.Tk):
    def __init__(self, modelo_path, num_pisos, vel_traslado, est_sistema):
        super().__init__()
        self.title("Simulador de Ascensores")
        self.geometry("600x600")
        self.num_pisos = num_pisos
        self.vel_traslado = vel_traslado
        self.est_sistema = est_sistema
        self.modelo = load_model(modelo_path)

        self.ascensores = [
            Ascensor("Ascensor 1", num_pisos),
            Ascensor("Ascensor 2", num_pisos)
        ]

        self.crear_widgets()
        self.actualizar_ui()

    def crear_widgets(self):
        # Panel ascensores
        self.frame_ascensores = tk.Frame(self)
        self.frame_ascensores.pack(side=tk.LEFT, padx=10, pady=10)

        self.labels_ascensores = []
        for asc in self.ascensores:
            frame = tk.LabelFrame(self.frame_ascensores, text=asc.nombre, padx=10, pady=10)
            frame.pack(pady=10, fill="x")

            label_estado = tk.Label(frame, text="", justify="left", font=("Consolas", 10))
            label_estado.pack()
            self.labels_ascensores.append(label_estado)

        self.frame_botones = tk.Frame(self)
        self.frame_botones.pack(side=tk.LEFT, padx=20, pady=10)

        tk.Label(self.frame_botones, text="Llamadas por Piso:", font=("Arial", 12, "bold")).pack(pady=5)

        for piso in range(self.num_pisos - 1, -1, -1):
            frame_piso = tk.Frame(self.frame_botones)
            frame_piso.pack(pady=2, fill="x")

            lbl_piso = tk.Label(frame_piso, text=f"Piso {piso + 1}", width=6)
            lbl_piso.pack(side=tk.LEFT)

            # Botón subir
            if piso < self.num_pisos - 1:
                btn_subir = tk.Button(frame_piso, text="↑", width=3,
                                      command=lambda p=piso: self.llamar_ascensor(p, "subir"))
                btn_subir.pack(side=tk.LEFT, padx=2)
            else:
                tk.Label(frame_piso, text="  ").pack(side=tk.LEFT, padx=5)

            # Botón bajar
            if piso > 0:
                btn_bajar = tk.Button(frame_piso, text="↓", width=3,
                                      command=lambda p=piso: self.llamar_ascensor(p, "bajar"))
                btn_bajar.pack(side=tk.LEFT, padx=2)
            else:
                tk.Label(frame_piso, text="  ").pack(side=tk.LEFT, padx=5)

        #Boton para detener el sistema
        self.btn_toggle_sistema = tk.Button(self, text="Detener Sistema" if self.est_sistema else "Activar Sistema",
                                            command=self.toggle_sistema)
        self.btn_toggle_sistema.pack(pady=5)

    def toggle_sistema(self):
        self.destroy()

    def llamar_ascensor(self, piso_llamada, direccion_llamada):
        dir_llamada = 1 if direccion_llamada == "subir" else -1

        def dir_texto_a_num(dir_texto):
            if dir_texto.lower() == "subiendo":
                return 1
            elif dir_texto.lower() == "bajando":
                return -1
            else:
                return 0

        def estimar_tiempo(piso_actual, direccion_actual, piso_llamada, destinos_pendientes, direccion_llamada,
                           vel_traslado):
            penalizacion_destinos = 2  # segundos extra por cada destino pendiente
            if direccion_actual != 0 and direccion_actual != direccion_llamada:
                penalizacion_direccion = 50
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

        datos_asc = []
        for asc in self.ascensores:
            dir_actual = dir_texto_a_num(asc.direccion)
            destinos_pend = len(asc.destinos)
            personas_dentro = asc.personas_dentro

            tiempo_est = estimar_tiempo(
                asc.piso_actual,
                dir_actual,
                piso_llamada,
                destinos_pend,
                dir_llamada,
                self.vel_traslado
            )

            datos_asc.append({
                "piso_actual": asc.piso_actual,
                "direccion_actual": dir_actual,
                "destinos_pendientes": destinos_pend,
                "personas_dentro": personas_dentro,
                "tiempo_estimado": tiempo_est
            })

        entrada = np.array([[
            piso_llamada,
            dir_llamada,
            datos_asc[0]["piso_actual"],
            datos_asc[1]["piso_actual"],
            datos_asc[0]["direccion_actual"],
            datos_asc[1]["direccion_actual"],
            datos_asc[0]["destinos_pendientes"],
            datos_asc[1]["destinos_pendientes"],
            datos_asc[0]["personas_dentro"],
            datos_asc[1]["personas_dentro"],
            datos_asc[0]["tiempo_estimado"],
            datos_asc[1]["tiempo_estimado"],
            self.num_pisos
        ]])

        pred = self.modelo.predict(entrada, verbose=1)

        prob = pred[0][0]
        ascensor_seleccionado = 1 if prob > 0.5 else 0

        print("Entrada:", entrada)
        print("Predicción raw:", pred)
        print("Probabilidad:", prob)

        asc_sel = self.ascensores[ascensor_seleccionado]
        if piso_llamada not in asc_sel.destinos:
            asc_sel.destinos.append(piso_llamada)

        tiempo = datos_asc[ascensor_seleccionado]["tiempo_estimado"]
        precision = prob if ascensor_seleccionado == 1 else 1 - prob
        precision_pct = precision * 100
        # Mostrar resultado en popup
        msg = (
            f"Ascensor seleccionado: {asc_sel.nombre}\n"
            f"Piso llamado: {piso_llamada + 1}\n"
            f"Tiempo estimado de llegada: {tiempo} segundos\n"
            f"Precisión de selección (probabilidad): {precision_pct:.2f}%"
        )
        respuesta = messagebox.askyesno("Selección de Ascensor", msg + "\n\n¿Desea simular otro caso?")

        if not respuesta:
            self.destroy()
        else:
            for asc in self.ascensores:
                asc.reset_estado()
            self.actualizar_ui()

    def actualizar_ui(self):
        for i, asc in enumerate(self.ascensores):
            self.labels_ascensores[i].config(text=asc.actualizar_estado())


def iniciar_ui(modelo_path, num_pisos, vel_traslado, est_sistema):
    app = InterfazAscensores(modelo_path, num_pisos, vel_traslado, est_sistema)
    app.mainloop()
