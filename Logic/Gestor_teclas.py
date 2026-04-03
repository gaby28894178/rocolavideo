import configparser
import os

class GestorTeclas:
    def __init__(self):
        self.ruta_config = 'config.ini'
        self.config = configparser.ConfigParser()
        self.campos_teclas = ['arriba', 'abajo', 'izquierda', 'derecha', 'pag_siguiente', 'pag_anterior', 'enter', 'seleccion', 'credito']
        self.lista_maestra = ["UP", "DOWN", "LEFT", "RIGHT", "RETURN", "SPACE", "N", "G", "C", "ESCAPE", "F10", "MODO ESCUCHA"]
        self.cargar_config()

    def cargar_config(self):
        if not os.path.exists(self.ruta_config):
            self.config['TECLAS'] = {k: 'N/A' for k in self.campos_teclas}
            self.config['SISTEMA'] = {'estado_rocola': 'LIBRE', 'ruta_contenidos': 'C:/musica'}
            self.config['ESTADISTICAS'] = {'total_reproducciones': '0'}
            self.guardar_archivo()
        else:
            self.config.read(self.ruta_config)
            if 'ESTADISTICAS' not in self.config:
                self.config['ESTADISTICAS'] = {'total_reproducciones': '0'}
                self.guardar_archivo()

    def guardar(self, seccion, clave, valor):
        if seccion not in self.config: self.config[seccion] = {}
        self.config[seccion][clave] = str(valor)
        self.guardar_archivo()

    def sumar_reproduccion(self):
        actual = int(self.config['ESTADISTICAS'].get('total_reproducciones', '0'))
        self.guardar('ESTADISTICAS', 'total_reproducciones', str(actual + 1))

    def guardar_archivo(self):
        with open(self.ruta_config, 'w') as f:
            self.config.write(f)