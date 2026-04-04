import os

class Disco:
    def __init__(self, nombre, ruta, portada, archivos, tipo):
        self.nombre = nombre
        self.ruta = ruta
        self.portada = portada
        self.archivos = archivos
        self.tipo = tipo
        self.textura = None # Se carga en el Explorador para no saturar la memoria

class MotorBiblioteca:
    def __init__(self):
        # Definimos los formatos que soporta la Fonola
        self.formatos_audio = ('.mp3', '.wav', '.wma', '.ogg')
        self.formatos_video = ('.mp4', '.avi', '.mkv', '.mpg', '.wmv', '.flv')
        self.formatos_fotos = ('.jpg', '.jpeg', '.png', '.bmp')

    def cargar_coleccion(self, ruta_raiz):
        coleccion = []
        
        # Verificamos si la ruta existe antes de empezar
        if not os.path.exists(ruta_raiz): 
            print(f"[!] Error: La ruta {ruta_raiz} no existe.")
            return []

        try:
            # Listamos las carpetas de música/video (Artistas o Álbumes)
            for nombre_carpeta in os.listdir(ruta_raiz):
                ruta_completa = os.path.join(ruta_raiz, nombre_carpeta)
                
                if os.path.isdir(ruta_completa):
                    try:
                        # Intentamos leer el contenido de la carpeta
                        todos_los_archivos = os.listdir(ruta_completa)
                        
                        # 1. Buscamos la Portada (Imagen)
                        tapa = None
                        for f in todos_los_archivos:
                            if f.lower().endswith(self.formatos_fotos):
                                tapa = os.path.join(ruta_completa, f)
                                break
                        
                        # Si no hay imagen, usamos la de "sin portada" por defecto
                        if not tapa:
                            tapa = "Interface/img/sin_tapa.png"

                        # 2. Filtramos temas: Unimos Audio y Video en una sola lista
                        # Esto permite que aparezcan juntos y sigan el orden de la cola
                        lista_temas = [
                            f for f in todos_los_archivos 
                            if f.lower().endswith(self.formatos_audio + self.formatos_video)
                        ]
                        
                        # 3. Clasificamos el disco
                        if lista_temas:
                            # Si tiene al menos un video, lo marcamos como "Video" para el icono del Explorador
                            es_video = any(f.lower().endswith(self.formatos_video) for f in lista_temas)
                            tipo = "Video" if es_video else "Audio"
                            
                            nuevo_disco = Disco(
                                nombre=nombre_carpeta, 
                                ruta=ruta_completa, 
                                portada=tapa, 
                                archivos=lista_temas, 
                                tipo=tipo
                            )
                            
                            coleccion.append(nuevo_disco)
                            print(f"[BIBLIOTECA] Cargado: {nombre_carpeta} ({tipo})")
                            
                    except PermissionError:
                        print(f"[ADVERTENCIA] Sin permisos para acceder a: {nombre_carpeta}")
                    except Exception as e:
                        print(f"[!] Error procesando {nombre_carpeta}: {e}")

        except Exception as e:
            print(f"[CRÍTICO] Error al acceder a la ruta raíz de contenidos: {e}")
        
        return coleccion