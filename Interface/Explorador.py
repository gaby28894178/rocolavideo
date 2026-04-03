import pygame
import os
import math
import subprocess

class ExploradorMultimedia:
    def __init__(self, surface, gestor, coleccion):
        self.surface = surface
        self.gestor = gestor
        self.coleccion = coleccion
        self.indice_sel = 0
        self.creditos = 0
        self.fuente = pygame.font.SysFont("Consolas", 18, bold=True)
        self.fuente_cola = pygame.font.SysFont("Consolas", 14, bold=True)
        
        self.cols, self.filas = 5, 3
        self.ancho_p, self.alto_p = surface.get_size()
        self.ancho_item, self.alto_item = 156, 156 
        self.margen_v, self.margen_h = 80, 55
        
        self.estado = "GRID" 
        self.timer_anim = 0
        self.disco_sel = None
        self.vista_lista = None
        self.cola_nombres = []

        ruta_bg = os.path.join("Interface", "img", "base_background.png")
        self.background = None
        if os.path.exists(ruta_bg):
            try:
                img_bg = pygame.image.load(ruta_bg).convert()
                self.background = pygame.transform.smoothscale(img_bg, (self.ancho_p, self.alto_p))
            except: pass

    def manejar_eventos(self, eventos):
        t = self.gestor.config['TECLAS']
        modo = self.gestor.config['SISTEMA'].get('estado_rocola', 'LIBRE')

        for event in eventos:
            if event.type == pygame.KEYDOWN:
                tecla = pygame.key.name(event.key).upper()

                if self.estado == "GRID":
                    if tecla == t.get('derecha').upper(): self.indice_sel = (self.indice_sel + 1) % len(self.coleccion)
                    elif tecla == t.get('izquierda').upper(): self.indice_sel = (self.indice_sel - 1) % len(self.coleccion)
                    elif tecla == t.get('abajo').upper(): self.indice_sel = (self.indice_sel + self.cols) % len(self.coleccion)
                    elif tecla == t.get('arriba').upper(): self.indice_sel = (self.indice_sel - self.cols) % len(self.coleccion)
                    elif tecla == t.get('credito').upper(): self.creditos += 1
                    elif tecla == t.get('enter').upper():
                        if (modo == 'LIBRE' or self.creditos > 0) and self.coleccion:
                            self.estado = "ANIMATING"
                            self.timer_anim = pygame.time.get_ticks()
                            self.disco_sel = self.coleccion[self.indice_sel]

                elif self.estado == "LIST" and self.vista_lista:
                    if tecla == t.get('pag_anterior').upper() or tecla == "ESCAPE":
                        self.estado = "GRID"
                    else:
                        self.vista_lista.manejar_eventos(tecla, t, self.cola_nombres)

    def dibujar_grilla(self):
        if self.estado in ["GRID", "ANIMATING"]:
            if self.background: self.surface.blit(self.background, (0,0))
            else: self.surface.fill((10, 10, 20))

            if not self.coleccion: return

            inicio = (self.indice_sel // 15) * 15
            items = self.coleccion[inicio : inicio + 15]
            sel_data = None

            for i, disco in enumerate(items):
                x = self.margen_h + (i % self.cols) * (self.ancho_item + 35)
                y = self.margen_v + (i // 5) * (self.alto_item + 35)
                if disco.textura is None: self.cargar_img(disco)
                
                if (i + inicio) == self.indice_sel: sel_data = (disco, x, y)
                else: self.dibujar_caja(disco.textura, pygame.Rect(x, y, self.ancho_item, self.alto_item))

            if sel_data:
                disco, x, y = sel_data
                img, rect = disco.textura, pygame.Rect(x, y, self.ancho_item, self.alto_item)
                
                if self.estado == "ANIMATING":
                    dt = pygame.time.get_ticks() - self.timer_anim
                    # --- CAMBIO: Animación de 800ms (0.8 seg) ---
                    duracion = 800 
                    if dt < duracion:
                        f = 1.0 + (0.50 * (dt/duracion)) # Zoom más controlado
                        img = pygame.transform.smoothscale(disco.textura, (int(self.ancho_item*f), int(self.alto_item*f)))
                        rect = img.get_rect(center=rect.center)
                        # Movimiento más lento y suave
                        rect.y += math.sin(dt * 0.008) * 15 
                    else:
                        self.vista_lista = VistaCD(self.surface, self.disco_sel, self.fuente, self.gestor)
                        self.estado = "LIST"
                else:
                    c = [(255,0,255), (0,255,255), (255,255,0)][(pygame.time.get_ticks()//150)%3]
                    pygame.draw.rect(self.surface, c, rect.inflate(15, 15), 5, border_radius=8)
                
                self.dibujar_caja(img, rect)
            self.dibujar_barra_inferior()

        elif self.estado == "LIST" and self.vista_lista:
            self.vista_lista.dibujar()
            if self.vista_lista.debe_volver: 
                self.estado = "GRID"
                if self.gestor.config['SISTEMA'].get('estado_rocola') == 'CREDITO':
                    self.creditos = max(0, self.creditos - 1)

    def dibujar_caja(self, img, rect):
        pygame.draw.rect(self.surface, (50, 50, 50), rect.inflate(4, 4), 2)
        self.surface.blit(img, rect)
        pygame.draw.rect(self.surface, (230, 230, 230), rect, 1)
        ref = pygame.Surface((rect.width // 4, rect.height), pygame.SRCALPHA)
        ref.fill((255, 255, 255, 35))
        self.surface.blit(ref, (rect.x, rect.y))

    def cargar_img(self, d):
        try:
            d.textura = pygame.transform.smoothscale(pygame.image.load(d.portada).convert_alpha(), (self.ancho_item, self.alto_item))
        except:
            d.textura = pygame.Surface((self.ancho_item, self.alto_item)); d.textura.fill((60,60,60))

    def dibujar_barra_inferior(self):
        c = [(255,0,255), (0,255,255), (255,255,0)][(pygame.time.get_ticks()//150)%3]
        r = pygame.Rect(self.margen_h, self.alto_p - 75, 910, 50)
        pygame.draw.rect(self.surface, c, r, 2, border_radius=10)
        modo = self.gestor.config['SISTEMA'].get('estado_rocola', 'LIBRE')
        txt_m = f"CREDITOS: {self.creditos}" if modo == "CREDITO" else "MODO: FREE"
        self.surface.blit(self.fuente.render(txt_m, True, (255, 255, 255)), (r.x + 15, r.y + 12))
        cola = " | SIGUE: " + (" / ".join(self.cola_nombres[:2]) if self.cola_nombres else "VACIA")
        self.surface.blit(self.fuente_cola.render(cola, True, c), (r.x + 180, r.y + 15))



#! Vistas de  selector de temas 
class VistaCD:
    def __init__(self, surface, disco, fuente, gestor):
        self.surface, self.disco, self.fuente, self.gestor = surface, disco, fuente, gestor
        self.sel, self.scroll, self.play, self.timer = 0, 0, False, 0
        self.debe_volver = False 
        self.ancho_p, self.alto_p = surface.get_size()
        
        try:
            img_orig = pygame.image.load(disco.portada).convert()
            # 1. Ratio base para cubrir la pantalla
            ratio = max(self.ancho_p / img_orig.get_width(), self.alto_p / img_orig.get_height())
            img_escalada = pygame.transform.smoothscale(img_orig, (int(img_orig.get_width()*ratio), int(img_orig.get_height()*ratio)))
            
            # 2. AJUSTE DE BORDES (REDUCCIÓN AGRESIVA):
            # 20% Arriba y Abajo (Factor 0.80) -> 10% que pediste + 10% que ya estaba
            # 3% Izquierda y Derecha (Factor 0.97) para que no se pegue
            nuevo_ancho = int(img_escalada.get_width() * 0.97)
            nuevo_alto = int(img_escalada.get_height() * 0.80)
            
            self.bg_final = pygame.transform.smoothscale(img_escalada, (nuevo_ancho, nuevo_alto))
            
        except:
            self.bg_final = pygame.Surface((int(self.ancho_p*0.97), int(self.alto_p*0.80)))
            self.bg_final.fill((30,30,30))

        # El overlay se ajusta al nuevo tamaño de la imagen con el 20% de aire
        self.overlay = pygame.Surface(self.bg_final.get_size(), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 110)) 

    def manejar_eventos(self, tecla, t, cola_nombres):
        """Maneja la navegación por la lista de temas"""
        if not self.play:
            cant = len(self.disco.archivos)
            if tecla == t.get('abajo').upper(): 
                self.sel = (self.sel + 1) % cant
            elif tecla == t.get('arriba').upper(): 
                self.sel = (self.sel - 1) % cant
            elif tecla == t.get('enter').upper():
                self.reproducir(cola_nombres)
            
            # Control de scroll dinámico
            if self.sel > 12:
                self.scroll = (self.sel - 12) * 40
            else:
                self.scroll = 0

    def reproducir(self, cola_nombres):
        """Envía el tema seleccionado a la cola o al reproductor"""
        self.play = True
        self.timer = pygame.time.get_ticks()
        nombre_tema = self.disco.archivos[self.sel]
        path = os.path.normpath(os.path.join(self.disco.ruta, nombre_tema))
        ext = nombre_tema.lower().split('.')[-1]
        
        try: self.gestor.sumar_reproduccion()
        except: pass

        if ext in ['mp4', 'avi', 'mkv', 'mov', 'mpg']:
            try:
                pygame.mixer.music.stop()
                vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
                if not os.path.exists(vlc_path):
                    vlc_path = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
                
                if os.path.exists(vlc_path):
                    cmd = f'"{vlc_path}" "{path}" --fullscreen --play-and-exit --no-video-title-show'
                    subprocess.Popen(cmd, shell=True)
                else: os.startfile(path)
            except: os.startfile(path)
        else:
            try:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.play()
                else:
                    pygame.mixer.music.queue(path)
                    cola_nombres.append(nombre_tema[:20])
            except: pass

    def dibujar(self):
        # Fondo negro sólido para el marco "Cinemascope"
        self.surface.fill((0,0,0))
        
        # Dibujamos la portada achicada un 20% en el alto
        rect_bg = self.bg_final.get_rect(center=(self.ancho_p//2, self.alto_p//2))
        self.surface.blit(self.bg_final, rect_bg)
        self.surface.blit(self.overlay, rect_bg)
        
        # Lista de canciones con sombra
        for i, tema in enumerate(self.disco.archivos):
            y = 100 + (i * 40) - self.scroll
            if 80 < y < 680:
                color = (255, 255, 255)
                if i == self.sel:
                    # Selección con color animado
                    c = [(255,0,255), (0,255,255), (255,255,0)][(pygame.time.get_ticks()//150)%3]
                    pygame.draw.rect(self.surface, c, (50, y-5, 920, 40), 2, border_radius=5)
                    color = c
                
                # Renderizado de texto
                sombra = self.fuente.render(f"{i+1:02d}. {tema[:70]}", True, (0, 0, 0))
                self.surface.blit(sombra, (77, y + 2))
                txt = self.fuente.render(f"{i+1:02d}. {tema[:70]}", True, color)
                self.surface.blit(txt, (75, y))
        
        if self.play:
            # Notificación de cola
            pygame.draw.rect(self.surface, (0,0,0), (300, 690, 420, 40))
            self.surface.blit(self.fuente.render("¡AÑADIDO A LA COLA!", True, (0, 255, 0)), (380, 700))
            if pygame.time.get_ticks() - self.timer > 1200: 
                self.debe_volver = True