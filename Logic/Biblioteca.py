import os

class Disco:
    def __init__(self, nombre, ruta, portada, archivos, tipo):
        self.nombre = nombre
        self.ruta = ruta
        self.portada = portada
        self.archivos = archivos
        self.tipo = tipo
        self.textura = None # Para POO: la cargamos solo cuando se use en el Explorador

class MotorBiblioteca:
    def __init__(self):
        self.formatos_audio = ('.mp3', '.wav', '.wma')
        self.formatos_video = ('.mp4', '.avi', '.mkv', '.mpg')
        self.formatos_fotos = ('.jpg', '.jpeg', '.png')

    def cargar_coleccion(self, ruta_raiz):
        coleccion = []
        if not os.path.exists(ruta_raiz): 
            print(f"[!] Error: La ruta {ruta_raiz} no existe.")
            return []

        try:
            for nombre_carpeta in os.listdir(ruta_raiz):
                ruta_completa = os.path.join(ruta_raiz, nombre_carpeta)
                
                if os.path.isdir(ruta_completa):
                    try:
                        # --- EL ARREGLO ESTÁ ACÁ ---
                        # Intentamos listar, si Windows dice que no, saltamos al except
                        todos_los_archivos = os.listdir(ruta_completa)
                        
                        tapa = None
                        for f in todos_los_archivos:
                            if f.lower().endswith(self.formatos_fotos):
                                tapa = os.path.join(ruta_completa, f)
                                break
                        
                        if not tapa:
                            tapa = "Interface/img/sin_tapa.png"

                        lista_temas = [f for f in todos_los_archivos if f.lower().endswith(self.formatos_audio + self.formatos_video)]
                        
                        if lista_temas:
                            tipo = "Video" if any(f.lower().endswith(self.formatos_video) for f in lista_temas) else "Audio"
                            nuevo_disco = Disco(nombre_carpeta, ruta_completa, tapa, lista_temas, tipo)
                            coleccion.append(nuevo_disco)
                            print(f"[BIBLIOTECA] Cargado: {nombre_carpeta}")
                            
                    except PermissionError:
                        print(f"[ADVERTENCIA] Saltando carpeta sin permiso: {nombre_carpeta}")
                    except Exception as e:
                        print(f"[!] Error en carpeta {nombre_carpeta}: {e}")
        except Exception as e:
            print(f"[CRÍTICO] Error al acceder a la ruta raíz: {e}")
        
        return coleccion