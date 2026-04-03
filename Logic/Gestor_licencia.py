import requests
import uuid
import socket
import configparser

class GestorLicencia: # Nombre exacto que busca tu main.py
    def __init__(self, config_file='url.ini'):
        self.config = configparser.ConfigParser()
        try:
            # Leemos la URL desde el archivo url.ini
            self.config.read(config_file)
            self.url_base = self.config['SERVIDOR'].get('url', 'http://localhost/fonola/api/validar.php')
        except:
            # Si el archivo ini no existe o falla, usamos esta por defecto
            self.url_base = "http://localhost/fonola/api/validar.php"

    def obtener_mac(self):
        """Obtiene la MAC real de la PC"""
        try:
            mac_num = uuid.getnode()
            mac_hex = ':'.join(['{:02x}'.format((mac_num >> ele) & 0xff) for ele in range(0, 8*6, 8)][::-1])
            return mac_hex.upper()
        except:
            return "00:00:00:00:00:00"

    def validar_remoto(self, datos_hardware):
        """Metodo que llama tu main.py (linea 17)"""
        # Usamos la MAC que obtenemos nosotros para seguridad
        mac_actual = self.obtener_mac()
        nombre_pc = socket.gethostname()

        try:
            # Enviamos los datos al PHP
            params = {
                'mac': mac_actual,
                'pc': nombre_pc
            }
            
            print(f"[DEPURACIÓN] Conectando a: {self.url_base}")
            print(f"[DEPURACIÓN] Validando ID: {mac_actual}")

            response = requests.get(self.url_base, params=params, timeout=5)
            
            # El PHP devuelve un JSON: {"status": true} o {"status": false}
            resultado = response.json()

            if resultado.get('status') == True:
                print("[SISTEMA] Licencia activa. Iniciando...")
                return True
            else:
                print("[SISTEMA] Licencia inactiva o vencida.")
                return False

        except Exception as e:
            print(f"[DEPURACIÓN] Error de conexión o formato: {e}")
            return False