import pygame
import os
import math
import subprocess
import sys

class ExploradorMultimedia:
    def __init__(self, surface, gestor, coleccion):
        self.surface = surface
        self.gestor = gestor
        self.coleccion = coleccion
        self.indice_sel = 0
        self.creditos = 0
        self.fuente = pygame.font.SysFont("Consolas", 18, bold=True)
        self.fuente_cola = pygame.font.SysFont("Consolas", 14, bold=True)
        self.fuente_onair = pygame.font.SysFont("Arial", 16, bold=True)
        
        # --- CONFIGURACIÓN DESDE EL INI ---
        conf_sis = self.gestor.config['SISTEMA']
        self.cols = int(conf_sis.get('columnas', 5))
        self.filas = int(conf_sis.get('filas', 3))
        self.items_por_pagina = self.cols * self.filas
        self.barra_alto = int(conf_sis.get('barra_grueso', 5))
        
        # Colores de la barra de tiempo
        try:
            self.color_visto = tuple(map(int, conf_sis.get('barra_color_visto', '255,255,255').split(',')))
            self.color_resto = tuple(map(int, conf_sis.get('barra_color_resto', '0,255,100').split(',')))
        except:
            self.color_visto, self.color_resto = (255, 255, 255), (0, 255, 100)

        # --- CARGA DEL FONDO DINÁMICO ---
        # Si no existe en el ini, busca por defecto en Interface/img/base_background.png
        ruta_bg = conf_sis.get('background', 'Interface/img/base_background.png')
        self.background = None
        if os.path.exists(ruta_bg):
            try:
                img_temp = pygame.image.load(ruta_bg).convert()
                self.background = pygame.transform.smoothscale(img_temp, surface.get_size())
            except: print(f"Error cargando fondo: {ruta_bg}")

        # --- VARIABLES DE ESTADO Y REPRODUCCIÓN ---
        self.ancho_p, self.alto_p = surface.get_size()
        self.ancho_item, self.alto_item = 156, 156 
        self.margen_v, self.margen_h = 110, 55 
        self.estado = "GRID" 
        self.timer_anim = 0
        self.disco_sel = None
        self.vista_lista = None
        
        # Variables críticas para evitar el AttributeError
        self.cola_rutas = []
        self.cola_nombres = []
        self.tema_actual = "" 
        self.reproduciendo_video = False 
        self.duracion_actual_segundos = 0 
        self.timer_inactividad = pygame.time.get_ticks()
        self.tiempo_espera_auto = 180000 # 3 min

        # --- PRE-CARGA DE SOMBRAS (De lejos/claro a cerca/oscuro) ---
        self.capas_sombra = [
            ((220, 220, 220, 30), 12, 10),
            ((190, 190, 190, 60), 8, 7),
            ((140, 140, 140, 90), 4, 4),
            ((80, 80, 80, 140), 0, 2)
        ]

        # --- MINI CD IRIDISCENTE ---
        self.mini_cd_base = pygame.Surface((40, 156), pygame.SRCALPHA)
        pygame.draw.circle(self.mini_cd_base, (160, 160, 165), (0, 78), 38)
        pygame.draw.circle(self.mini_cd_base, (210, 210, 215), (0, 78), 38, 1)
        
        # Reflejo de colores (Arcoíris)
        self.surf_reflejo = pygame.Surface((120, 120), pygame.SRCALPHA)
        colores = [(138,43,226,70), (0,0,255,60), (0,255,0,60), (255,255,0,70), (255,0,0,50)]
        for i, col in enumerate(colores):
            ang = i * 72
            puntos = [(60,60)]
            for a in range(ang, ang + 45, 5):
                rad = math.radians(a)
                puntos.append((60 + 55 * math.cos(rad), 60 + 55 * math.sin(rad)))
            puntos.append((60,60))
            pygame.draw.polygon(self.surf_reflejo, col, puntos)

    def manejar_eventos(self, eventos):
        t = self.gestor.config['TECLAS']
        modo = self.gestor.config['SISTEMA'].get('estado_rocola', 'LIBRE')
        for event in eventos:
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                self.timer_inactividad = pygame.time.get_ticks()
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
                    if tecla == t.get('pag_anterior').upper() or tecla == "ESCAPE": self.estado = "GRID"
                    else: self.vista_lista.manejar_eventos(tecla, t, self.cola_rutas, self.cola_nombres)

    def lanzar_reproduccion(self, ruta):
        ext = ruta.lower().split('.')[-1]
        self.tema_actual = os.path.basename(ruta).upper()
        if ext in ['mp4', 'avi', 'mkv', 'mpg', 'mov']:
            self.reproduciendo_video = True
            pygame.mixer.music.pause()
            try:
                mpc = r"C:\Program Files\K-Lite Codec Pack\MPC-HC64\mpc-hc64.exe"
                if not os.path.exists(mpc): mpc = r"C:\Program Files (x86)\K-Lite Codec Pack\MPC-HC64\mpc-hc64.exe"
                if os.path.exists(mpc): subprocess.run([mpc, ruta, "/fullscreen", "/play", "/close"], check=False)
                else: subprocess.run(f'"{ruta}"', shell=True)
            except: pass
            self.reproduciendo_video = False
            self.tema_actual = ""
        else:
            try:
                sonido = pygame.mixer.Sound(ruta)
                self.duracion_actual_segundos = sonido.get_length()
                pygame.mixer.music.load(ruta)
                pygame.mixer.music.play()
            except: pass

    def revisar_cola(self):
        if not self.reproduciendo_video:
            if not pygame.mixer.music.get_busy() and self.cola_rutas:
                proximo = self.cola_rutas.pop(0)
                self.cola_nombres.pop(0)
                self.lanzar_reproduccion(proximo)
            elif not pygame.mixer.music.get_busy() and not self.cola_rutas:
                self.tema_actual = ""

    def dibujar_caja(self, img, rect, seleccionado=False):
        # 1. Sombras dinámicas
        for col, grow, off in self.capas_sombra:
            s = pygame.Surface((rect.width + grow, rect.height + grow), pygame.SRCALPHA)
            pygame.draw.rect(s, col, (0, 0, s.get_width(), s.get_height()), border_radius=10)
            self.surface.blit(s, (rect.x + off, rect.y + off))

        # 2. Mini CD Giratorio
        if seleccionado:
            angulo = (pygame.time.get_ticks() // 4) % 360
            cd_f = self.mini_cd_base.copy()
            ref_r = pygame.transform.rotate(self.surf_reflejo, angulo)
            cd_f.blit(ref_r, ref_r.get_rect(center=(0, 78)))
            pygame.draw.circle(cd_f, (25, 25, 25), (0, 78), 11)
            off_cd = 8 + int(math.sin(pygame.time.get_ticks() * 0.005) * 2)
            cd_s = pygame.transform.smoothscale(cd_f, (int(rect.width * 0.22), rect.height))
            self.surface.blit(cd_s, (rect.right - 5 + off_cd, rect.y))

        # 3. Imagen y Bisagra
        self.surface.blit(img, rect)
        g_b = int(rect.width * 0.10)
        rect_b = pygame.Rect(rect.x, rect.y, g_b, rect.height)
        pygame.draw.rect(self.surface, (12, 12, 12), rect_b)
        for yr in range(rect.y + 4, rect.bottom - 4, 4):
            pygame.draw.line(self.surface, (30, 30, 30), (rect.x+2, yr), (rect_b.right-4, yr), 1)
        pygame.draw.rect(self.surface, (100, 100, 100), rect_b, 1)
        pygame.draw.rect(self.surface, (235, 235, 235), rect, 1)

    def cargar_img(self, d):
        try: d.textura = pygame.transform.smoothscale(pygame.image.load(d.portada).convert_alpha(), (self.ancho_item, self.alto_item))
        except: d.textura = pygame.Surface((self.ancho_item, self.alto_item)); d.textura.fill((50,50,50))

    def dibujar_grilla(self):
        self.revisar_cola()
        ahora = pygame.time.get_ticks()
        if self.estado == "GRID" and ahora - self.timer_inactividad > self.tiempo_espera_auto:
            self.indice_sel = (self.indice_sel + self.items_por_pagina) % len(self.coleccion)
            self.timer_inactividad = ahora

        if self.estado in ["GRID", "ANIMATING"]:
            if self.background: self.surface.blit(self.background, (0,0))
            else: self.surface.fill((10, 10, 20))
            
            self.dibujar_barra_tiempo()
            self.dibujar_panel_superior()

            inicio = (self.indice_sel // self.items_por_pagina) * self.items_por_pagina
            items = self.coleccion[inicio : inicio + self.items_por_pagina]
            sel_data = None
            for i, disco in enumerate(items):
                x = self.margen_h + (i % self.cols) * (self.ancho_item + 35)
                y = self.margen_v + (i // self.cols) * (self.alto_item + 35)
                if disco.textura is None: self.cargar_img(disco)
                r_item = pygame.Rect(x, y, self.ancho_item, self.alto_item)
                if (i + inicio) == self.indice_sel: sel_data = (disco, r_item)
                else: self.dibujar_caja(disco.textura, r_item)

            if sel_data:
                disco, r_base = sel_data
                img, rect = disco.textura, r_base
                c_n = [(255,0,255), (0,255,255), (255,255,0)][(ahora//150)%3]
                if self.estado == "ANIMATING":
                    dt = ahora - self.timer_anim
                    if dt < 800:
                        f = 1.0 + (0.40 * (dt/800))
                        img = pygame.transform.smoothscale(disco.textura, (int(self.ancho_item*f), int(self.alto_item*f)))
                        rect = img.get_rect(center=r_base.center)
                    else:
                        self.vista_lista = VistaCD(self.surface, self.disco_sel, self.fuente, self.gestor, self)
                        self.estado = "LIST"
                pygame.draw.rect(self.surface, c_n, rect.inflate(15, 15), 5, border_radius=8)
                self.dibujar_caja(img, rect, seleccionado=True)
            self.dibujar_barra_inferior()

        elif self.estado == "LIST" and self.vista_lista:
            self.vista_lista.dibujar()
            if self.vista_lista.debe_volver: self.estado = "GRID"

    def dibujar_barra_tiempo(self):
        if self.tema_actual != "" and not self.reproduciendo_video and self.duracion_actual_segundos > 0:
            pos = pygame.mixer.music.get_pos() / 1000.0
            if pos > 0:
                prog = min(pos / self.duracion_actual_segundos, 1.0)
                pygame.draw.rect(self.surface, self.color_resto, (0, 0, self.ancho_p, self.barra_alto))
                pygame.draw.rect(self.surface, self.color_visto, (0, 0, int(self.ancho_p * prog), self.barra_alto))

    def dibujar_panel_superior(self):
        rect_sup = pygame.Rect(self.margen_h, 15 + self.barra_alto, 910, 40)
        c = [(255,0,255), (0,255,255), (255,255,0)][(pygame.time.get_ticks()//150)%3]
        panel = pygame.Surface((rect_sup.width, rect_sup.height), pygame.SRCALPHA); panel.fill((0, 0, 0, 140)) 
        self.surface.blit(panel, (rect_sup.x, rect_sup.y))
        esta = self.tema_actual != ""
        col = c if esta else (0, 255, 100)
        pygame.draw.rect(self.surface, col, rect_sup, 2, border_radius=5)
        txt = f"REPRODUCIENDO: {self.tema_actual[:70]}" if esta else "SISTEMA LISTO"
        r_txt = self.fuente_onair.render(txt, True, col if esta else (255, 255, 255))
        self.surface.blit(r_txt, r_txt.get_rect(center=rect_sup.center))

    def dibujar_barra_inferior(self):
        c = [(255,0,255), (0,255,255), (255,255,0)][(pygame.time.get_ticks()//150)%3]
        r = pygame.Rect(self.margen_h, self.alto_p - 75, 910, 50)
        pygame.draw.rect(self.surface, c, r, 2, border_radius=10)
        modo = self.gestor.config['SISTEMA'].get('estado_rocola', 'LIBRE')
        txt = f"CREDITOS: {self.creditos}" if modo == "CREDITO" else "MODO: FREE"
        self.surface.blit(self.fuente.render(txt, True, (255, 255, 255)), (r.x + 20, r.y + 12))
        cola = "SIGUE: " + (" / ".join(self.cola_nombres[:2]) if self.cola_nombres else "VACIA")
        self.surface.blit(self.fuente_cola.render(cola, True, c), (r.x + 220, r.y + 15))

class VistaCD:
    def __init__(self, surface, disco, fuente, gestor, explorador):
        self.surface, self.disco, self.fuente, self.gestor, self.explorador = surface, disco, fuente, gestor, explorador
        self.sel, self.scroll, self.play, self.timer, self.debe_volver = 0, 0, False, 0, False
        self.ancho_p, self.alto_p = surface.get_size()
        try:
            img = pygame.image.load(disco.portada).convert()
            self.bg = pygame.transform.smoothscale(img, (int(self.ancho_p*0.97), int(self.alto_p*0.80)))
        except: self.bg = pygame.Surface((100,100))
        self.overlay = pygame.Surface(self.bg.get_size(), pygame.SRCALPHA); self.overlay.fill((0, 0, 0, 180)) 

    def manejar_eventos(self, tecla, t, cr, cn):
        if not self.play:
            cant = len(self.disco.archivos)
            if tecla == t.get('abajo').upper(): self.sel = (self.sel + 1) % cant
            elif tecla == t.get('arriba').upper(): self.sel = (self.sel - 1) % cant
            elif tecla == t.get('enter').upper():
                ruta = os.path.normpath(os.path.join(self.disco.ruta, self.disco.archivos[self.sel]))
                cr.append(ruta); cn.append(self.disco.archivos[self.sel][:15])
                self.play = True; self.timer = pygame.time.get_ticks()
            if self.sel > 12: self.scroll = (self.sel - 12) * 40
            else: self.scroll = 0

    def dibujar(self):
        self.surface.fill((0,0,0))
        rect_bg = self.bg.get_rect(center=(self.ancho_p//2, self.alto_p//2))
        self.surface.blit(self.bg, rect_bg); self.surface.blit(self.overlay, rect_bg)
        self.explorador.dibujar_panel_superior()
        for i, tema in enumerate(self.disco.archivos):
            y = 100 + (i * 40) - self.scroll
            if 80 < y < 680:
                color = (255, 255, 255)
                if i == self.sel:
                    c = [(255,0,255), (0,255,255), (255,255,0)][(pygame.time.get_ticks()//150)%3]
                    pygame.draw.rect(self.surface, c, (50, y-5, 920, 40), 2, border_radius=5); color = c
                self.surface.blit(self.fuente.render(f"{i+1:02d}. {tema[:70]}", True, color) , (75, y))
        if self.play:
            pygame.draw.rect(self.surface, (0,0,0), (self.ancho_p//2 - 150, 680, 300, 50))
            self.surface.blit(self.fuente.render("¡AÑADIDO!", True, (0, 255, 0)), (self.ancho_p//2 - 40, 695))
            if pygame.time.get_ticks() - self.timer > 1000: self.debe_volver = True