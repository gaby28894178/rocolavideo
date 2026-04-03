import requests
import uuid
import socket
import configparser
import os
import sys

class GestorLicencia:
    def __init__(self, nombre_archivo='url.ini'):
        self.config = configparser.ConfigParser()
        self.url_base = None
        
        # --- RUTA ABSOLUTA ---
        # sys.argv[0] es el main.py. Esto garantiza que busque en la carpeta del proyecto.
        directorio_raiz = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.ruta_final = os.path.join(directorio_raiz, nombre_archivo)
        
        # Si no lo encuentra ahí, busca una carpeta arriba (fuera de constructor)
        if not os.path.exists(self.ruta_final):
            ruta_superior = os.path.join(os.path.dirname(directorio_raiz), nombre_archivo)
            if os.path.exists(ruta_superior):
                self.ruta_final = ruta_superior

        self.cargar_url()

    def cargar_url(self):
        if self.ruta_final and os.path.exists(self.ruta_final):
            try:
                self.config.read(self.ruta_final)
                if 'SERVIDOR' in self.config:
                    # El .strip() borra espacios o saltos de línea accidentales
                    url = self.config['SERVIDOR'].get('url', '').strip()
                    if url:
                        self.url_base = url
                        print(f"[LICENCIA] Archivo detectado en: {self.ruta_final}")
                        print(f"[LICENCIA] URL: {self.url_base}")
                    else:
                        print("[ERROR] La URL está vacía en url.ini")
                else:
                    print(f"[ERROR] No existe la sección [SERVIDOR] en {self.ruta_final}")
            except Exception as e:
                print(f"[ERROR] Error al procesar el archivo: {e}")
        else:
            print(f"[ERROR CRÍTICO] No se encontró el archivo de configuración.")

    def obtener_mac(self):
        try:
            mac_num = uuid.getnode()
            mac_hex = ':'.join(['{:02x}'.format((mac_num >> ele) & 0xff) for ele in range(0, 8*6, 8)][::-1])
            return mac_hex.upper()
        except:
            return "00:00:00:00:00:00"

    def validar_remoto(self, datos_hardware):
        if not self.url_base:
            print("[BLOQUEO] Sin configuración de servidor. Abortando.")
            return False

        mac_actual = self.obtener_mac()
        nombre_pc = socket.gethostname()

        try:
            params = {'mac': mac_actual, 'pc': nombre_pc}
            headers = {'User-Agent': 'FonolaGabySoft-Client'}
            
            response = requests.get(self.url_base, params=params, headers=headers, timeout=10)
            resultado = response.json()

            if resultado.get('status') == True:
                print("[SISTEMA] Licencia autorizada.")
                return True
            else:
                print(f"[DENEGADO] MAC no autorizada: {mac_actual}")
                return False
        except Exception as e:
            print(f"[ERROR] Fallo de conexión remota: {e}")
            return False