import pygame
import sys
import os

def recurso_path(relative_path):
    """ Obtiene la ruta absoluta de los recursos para PyInstaller y VS Code """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class VentanaConfig:
    def __init__(self, gestor):
        self.gestor = gestor
        self.fuente = pygame.font.SysFont("Consolas", 18)
        self.fuente_negrita = pygame.font.SysFont("Consolas", 22, bold=True)
        self.fila_seleccionada = 0    
        self.columna_combo = 0    
        self.editando = False
        self.escuchando_tecla = False 
        self.escribiendo_texto = False 
        self.opciones_modo = ["LIBRE", "CREDITO"]
        self.input_texto = "" 

    def abrir(self):
        res_x = int(self.gestor.config['SISTEMA'].get('res_x', 1024))
        res_y = int(self.gestor.config['SISTEMA'].get('res_y', 768))
        ventana_cfg = pygame.display.set_mode((750, 700))
        pygame.display.set_caption("CONFIGURACIÓN GABYSOFT")
        running = True
        while running:
            ventana_cfg.fill((30, 30, 40))
            self.dibujar_panel(ventana_cfg)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.KEYDOWN:
                    if self.escribiendo_texto:
                        if event.key == pygame.K_RETURN:
                            self.gestor.guardar('SISTEMA', 'nombre_fonola', self.input_texto)
                            self.escribiendo_texto = self.editando = False
                        elif event.key == pygame.K_BACKSPACE: self.input_texto = self.input_texto[:-1]
                        elif event.key == pygame.K_ESCAPE: self.escribiendo_texto = self.editando = False
                        else:
                            if len(self.input_texto) < 25: self.input_texto += event.unicode.upper()
                        continue
                    if self.escuchando_tecla:
                        nombre = pygame.key.name(event.key).upper()
                        idx = self.fila_seleccionada - 4
                        if idx >= 0: self.gestor.guardar('TECLAS', self.gestor.campos_teclas[idx], nombre)
                        self.escuchando_tecla = self.editando = False
                        continue
                    if event.key == pygame.K_F10 and not self.editando: running = False
                    elif not self.editando:
                        total_filas = 4 + len(self.gestor.campos_teclas)
                        if event.key == pygame.K_UP: self.fila_seleccionada = (self.fila_seleccionada - 1) % total_filas
                        elif event.key == pygame.K_DOWN: self.fila_seleccionada = (self.fila_seleccionada + 1) % total_filas
                        elif event.key == pygame.K_RETURN:
                            if self.fila_seleccionada == 2: self.gestor.resetear_reproducciones()
                            else:
                                self.editando = True
                                self.columna_combo = 0
                                if self.fila_seleccionada == 0:
                                    self.escribiendo_texto = True
                                    self.input_texto = self.gestor.config['SISTEMA'].get('nombre_fonola', '')
                    else: 
                        if event.key == pygame.K_ESCAPE: self.editando = False
                        elif event.key == pygame.K_LEFT: self.columna_combo -= 1
                        elif event.key == pygame.K_RIGHT: self.columna_combo += 1
                        elif event.key == pygame.K_RETURN:
                            if self.fila_seleccionada == 1:
                                self.gestor.guardar('SISTEMA', 'estado_rocola', self.opciones_modo[self.columna_combo % 2])
                                self.editando = False
                            elif self.fila_seleccionada >= 4:
                                sel = self.gestor.lista_maestra[self.columna_combo % len(self.gestor.lista_maestra)]
                                if sel == "MODO ESCUCHA": self.escuchando_tecla = True
                                else:
                                    self.gestor.guardar('TECLAS', self.gestor.campos_teclas[self.fila_seleccionada-4], sel)
                                    self.editando = False
            pygame.display.flip()
        pygame.display.set_mode((res_x, res_y))

    def dibujar_panel(self, surface):
        self.render_item(surface, 0, "NOMBRE DE FONOLA", 'SISTEMA', 'nombre_fonola')
        self.render_item(surface, 1, "MODO REPRODUCCIÓN", 'SISTEMA', 'estado_rocola')
        y_stats = 35 + (2 * 45)
        sel_stats = (self.fila_seleccionada == 2)
        col_stats = (255, 255, 0) if sel_stats else (0, 255, 255)
        surface.blit(self.fuente.render("TOTAL REPRODUCCIONES", True, col_stats), (40, y_stats))
        total = self.gestor.config['ESTADISTICAS'].get('total_reproducciones', '0')
        surface.blit(self.fuente.render(str(total), True, (255, 255, 255)), (365, y_stats))
        self.render_item(surface, 3, "CARPETA CONTENIDOS", 'SISTEMA', 'ruta_contenidos')
        for i, campo in enumerate(self.gestor.campos_teclas):
            self.render_item(surface, i + 4, f"TECLA {campo.upper()}", 'TECLAS', campo)

    def render_item(self, surface, index, label, seccion, clave):
        y = 35 + (index * 45)
        sel = (self.fila_seleccionada == index)
        color = (255, 255, 0) if sel else (200, 200, 200)
        surface.blit(self.fuente.render(label, True, color), (40, y))
        pygame.draw.rect(surface, (45, 45, 60), (350, y-5, 360, 30))
        if sel and self.editando:
            if self.escribiendo_texto: val, col = self.input_texto + "|", (255, 255, 0)
            elif self.escuchando_tecla: val, col = ">>> PULSA UNA TECLA <<<", (255, 165, 0)
            else:
                lista = self.opciones_modo if index == 1 else self.gestor.lista_maestra
                val, col = f"< {lista[self.columna_combo % len(lista)]} >", (0, 255, 0)
        else: val, col = self.gestor.config[seccion].get(clave, "N/A"), (255, 255, 255)
        surface.blit(self.fuente.render(str(val), True, col), (365, y))

    # --- LOADER: CONFIGURABLE DESDE EL INI ---
    def mostrar_loader(self, surface, ruta_logo, tiempo_ms=5000):
        # 1. Leer valores del INI (usamos valores por defecto si no existen)
        conf = self.gestor.config['SISTEMA']
        
        # Tiempo (reemplaza el que viene del main si existe en el ini)
        t_ms = int(conf.get('loader_tiempo', tiempo_ms))
        
        # Color (Convertimos el string "255,215,0" a una tupla de números)
        try:
            c_raw = conf.get('loader_color', '255,215,0')
            color_barra = tuple(map(int, c_raw.split(',')))
        except:
            color_barra = (255, 215, 0) # Amarillo por defecto

        # Grosor
        alto_b = int(conf.get('loader_grueso', 80))

        try:
            ruta_fondo = recurso_path("Interface/img/image_4.png")
            fondo = pygame.image.load(ruta_fondo)
            fondo = pygame.transform.scale(fondo, surface.get_size())
        except: fondo = None

        try:
            logo = pygame.image.load(ruta_logo)
            logo = pygame.transform.scale(logo, (450, 450))
        except: logo = None

        reloj = pygame.time.Clock()
        inicio = pygame.time.get_ticks()
        fuente_progreso = pygame.font.SysFont("Arial", 30, bold=True)

        while True:
            tiempo_actual = pygame.time.get_ticks() - inicio
            if tiempo_actual >= t_ms: break
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            if fondo: surface.blit(fondo, (0, 0))
            else: surface.fill((10, 10, 20))

            if logo:
                rect_logo = logo.get_rect(center=(surface.get_width()//2, surface.get_height()//2 - 80))
                surface.blit(logo, rect_logo)

            progreso = min(tiempo_actual / t_ms, 1.0)
            ancho_p = surface.get_width()
            y_b = surface.get_height() - alto_b

            # Dibujo de la barra
            pygame.draw.rect(surface, (0, 0, 0), (0, y_b, ancho_p, alto_b))
            pygame.draw.rect(surface, color_barra, (0, y_b, int(ancho_p * progreso), alto_b))

            txt_str = f"SISTEMA INICIANDO... {int(progreso * 100)}%"
            txt_principal = fuente_progreso.render(txt_str, True, (255, 255, 255))
            txt_sombra = fuente_progreso.render(txt_str, True, (0, 0, 0))
            txt_rect = txt_principal.get_rect(center=(ancho_p // 2, y_b + alto_b // 2))
            
            surface.blit(txt_sombra, (txt_rect.x + 2, txt_rect.y + 2))
            surface.blit(txt_principal, txt_rect)

            pygame.display.flip()
            reloj.tick(60)

    def pantalla_bloqueo(self, datos_hw):
        pantalla = pygame.display.set_mode((700, 500))
        pygame.display.set_caption("SISTEMA BLOQUEADO")
        fuente_tit = pygame.font.SysFont("Arial", 30, bold=True)
        while True:
            pantalla.fill((80, 0, 0))
            txt1 = fuente_tit.render("EQUIPO NO AUTORIZADO", True, (255, 255, 255))
            txt2 = self.fuente.render(f"ID HW: {datos_hw}", True, (255, 255, 0))
            txt3 = self.fuente.render("CONTACTE AL ADMINISTRADOR PARA ACTIVAR\nTEL:011-2167-4227", True, (200, 200, 200))
            pantalla.blit(txt1, (700//2 - txt1.get_width()//2, 100))
            pantalla.blit(txt2, (700//2 - txt2.get_width()//2, 220))
            pantalla.blit(txt3, (700//2 - txt3.get_width()//2, 350))
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            pygame.display.flip()