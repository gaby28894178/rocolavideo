import os

class ItemMultimeda:
    def __init__(self, ruta_carpeta):
        self.nombre = os.path.basename(ruta_carpeta)
        self.ruta = ruta_carpeta
        self.archivos = [f for f in os.listdir(ruta_carpeta) if f.lower().endswith(('.mp3', '.mp4', '.wav', '.mkv'))]
        self.tipo = "Video" if any(f.lower().endswith(('.mp4', '.mkv')) for f in self.archivos) else "Musica"
        
        # Buscar la tapa
        self.tapa_ruta = "Interface/img/sin_tapa.png"
        for f in os.listdir(ruta_carpeta):
            if f.lower().endswith(('.jpg', '.png', '.jpeg')):
                self.tapa_ruta = os.path.join(ruta_carpeta, f)
                break
        self.textura = None # Se carga en la Vista para no saturar memoria