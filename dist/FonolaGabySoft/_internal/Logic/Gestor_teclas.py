import configparser
import os

class GestorTeclas:
    def __init__(self):
        self.ruta_config = 'config.ini'
        self.config = configparser.ConfigParser()
        self.campos_teclas = ['arriba', 'abajo', 'izquierda', 'derecha', 'pag_siguiente', 'pag_anterior', 'enter', 'seleccion', 'credito']
        self.lista_maestra = ["UP", "DOWN", "LEFT", "RIGHT", "RETURN", "SPACE", "N", "G", "C", "ESCAPE", "F10"]
        self.cargar_config()

    def cargar_config(self):
        if not os.path.exists(self.ruta_config):
            # Configuración Inicial (Si el archivo no existe)
            self.config['TECLAS'] = {k: 'N/A' for k in self.campos_teclas}
            self.config['SISTEMA'] = {
                'nombre_fonola': 'FONOLA GABYSOFT', # <-- NUEVO
                'estado_rocola': 'LIBRE', 
                'ruta_contenidos': 'C:/musica',
                'res_x': '1024',
                'res_y': '720',
                'columnas': '5',
                'filas': '4',
                'fullscreen': 'NO',
                'auto_inicio': 'NO'
            }
            self.config['ESTADISTICAS'] = {'total_reproducciones': '0'}
            self.guardar_archivo()
        else:
            self.config.read(self.ruta_config)
            
            # Verificación de secciones y campos nuevos (para no perder datos)
            if 'SISTEMA' not in self.config: self.config['SISTEMA'] = {}
            if 'nombre_fonola' not in self.config['SISTEMA']:
                self.config['SISTEMA']['nombre_fonola'] = 'FONOLA GABYSOFT'
            
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

    # --- NUEVO MÉTODO PARA RESETEAR ---
    def resetear_reproducciones(self):
        """Pone el contador de la rocola a cero"""
        self.guardar('ESTADISTICAS', 'total_reproducciones', '0')
        print("[SISTEMA] Estadísticas reseteadas a cero.")

    def guardar_archivo(self):
        try:
            with open(self.ruta_config, 'w') as f:
                self.config.write(f)
        except Exception as e:
            print(f"[ERROR] No se pudo escribir en {self.ruta_config}: {e}")