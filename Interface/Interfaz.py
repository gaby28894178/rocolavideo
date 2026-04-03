import pygame
import sys
import os

class VentanaConfig:
    def __init__(self, gestor):
        self.gestor = gestor
        self.fuente = pygame.font.SysFont("Consolas", 18)
        self.fuente_negrita = pygame.font.SysFont("Consolas", 22, bold=True)
        self.fila_seleccionada = 0    
        self.columna_combo = 0    
        self.editando = False
        self.escuchando_tecla = False 
        self.opciones_modo = ["LIBRE", "CREDITO"]

    def mostrar_loader(self, surface, ruta_etiqueta, tiempo_ms=15000):
        dir_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_vinilo = os.path.join(dir_actual, "img", "vinilo.png")
        ruta_fondo = os.path.join(dir_actual, "img", "image_4.png")
        ancho_p, alto_p = surface.get_size()
        inicio = pygame.time.get_ticks()
        angulo = 0
        disco, fondo = None, None

        try:
            if os.path.exists(ruta_fondo):
                f_raw = pygame.image.load(ruta_fondo).convert()
                fondo = pygame.transform.smoothscale(f_raw, (ancho_p, int(alto_p * 0.85)))
            
            v = pygame.image.load(ruta_vinilo).convert_alpha()
            e = pygame.image.load(ruta_etiqueta).convert_alpha()
            tam = int(alto_p * 0.60)
            v = pygame.transform.smoothscale(v, (tam, tam))
            tam_e = int(tam * 0.38)
            e = pygame.transform.smoothscale(e, (tam_e, tam_e))
            
            mask = pygame.Surface((tam_e, tam_e), pygame.SRCALPHA)
            pygame.draw.circle(mask, (255, 255, 255, 255), (tam_e//2, tam_e//2), tam_e//2)
            eti = pygame.Surface((tam_e, tam_e), pygame.SRCALPHA)
            eti.blit(e, (0, 0))
            eti.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            
            disco = pygame.Surface((tam, tam), pygame.SRCALPHA)
            disco.blit(v, (0, 0))
            disco.blit(eti, ((tam-tam_e)//2, (tam-tam_e)//2))
        except Exception as err: print(f"Error loader: {err}")

        while True:
            pasado = pygame.time.get_ticks() - inicio
            if pasado >= tiempo_ms: break
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            surface.fill((0, 0, 0))
            if fondo: surface.blit(fondo, (0, 0))
            if disco:
                angulo = (angulo - 2) % 360
                rot = pygame.transform.rotate(disco, angulo)
                surface.blit(rot, rot.get_rect(center=(ancho_p//2, int(alto_p*0.85)//2)))

            y_b = alto_p - int(alto_p * 0.15)
            prog = min(pasado / tiempo_ms, 1.0)
            pygame.draw.rect(surface, (30, 30, 30), (0, y_b, ancho_p, int(alto_p * 0.15)))
            pygame.draw.rect(surface, (0, 150, 255), (0, y_b, int(ancho_p * prog), int(alto_p * 0.15)))
            
            txt = self.fuente_negrita.render("GABYSOFT ENTERTAINMENT - CARGANDO CONTENIDO...", True, (255, 255, 255))
            surface.blit(txt, (ancho_p//2 - txt.get_width()//2, y_b + 40))
            pygame.display.flip()

    def abrir(self):
        ancho_orig, alto_orig = 1024, 768
        ventana_cfg = pygame.display.set_mode((750, 700))
        running = True
        while running:
            ventana_cfg.fill((30, 30, 40))
            self.dibujar_panel(ventana_cfg)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.KEYDOWN:
                    if self.escuchando_tecla:
                        nombre = pygame.key.name(event.key).upper()
                        idx = self.fila_seleccionada - 3
                        if idx >= 0: self.gestor.guardar('TECLAS', self.gestor.campos_teclas[idx], nombre)
                        self.escuchando_tecla = self.editando = False
                        continue
                    if event.key == pygame.K_F10 and not self.editando: running = False
                    elif not self.editando:
                        total = 3 + len(self.gestor.campos_teclas)
                        if event.key == pygame.K_UP: self.fila_seleccionada = (self.fila_seleccionada - 1) % total
                        elif event.key == pygame.K_DOWN: self.fila_seleccionada = (self.fila_seleccionada + 1) % total
                        elif event.key == pygame.K_RETURN and self.fila_seleccionada != 1: 
                            self.editando = True
                            self.columna_combo = 0
                    else:
                        if event.key == pygame.K_ESCAPE: self.editando = False
                        elif event.key == pygame.K_LEFT: self.columna_combo -= 1
                        elif event.key == pygame.K_RIGHT: self.columna_combo += 1
                        elif event.key == pygame.K_RETURN:
                            if self.fila_seleccionada == 0:
                                self.gestor.guardar('SISTEMA', 'estado_rocola', self.opciones_modo[self.columna_combo % 2])
                                self.editando = False
                            elif self.fila_seleccionada >= 3:
                                sel = self.gestor.lista_maestra[self.columna_combo % len(self.gestor.lista_maestra)]
                                if sel == "MODO ESCUCHA": self.escuchando_tecla = True
                                else:
                                    self.gestor.guardar('TECLAS', self.gestor.campos_teclas[self.fila_seleccionada-3], sel)
                                    self.editando = False
            pygame.display.flip()
        pygame.display.set_mode((ancho_orig, alto_orig))

    def dibujar_panel(self, surface):
        self.render_item(surface, 0, "MODO REPRODUCCIÓN", 'SISTEMA', 'estado_rocola')
        y_cont = 35 + 45
        total = self.gestor.config['ESTADISTICAS'].get('total_reproducciones', '0')
        surface.blit(self.fuente.render("TOTAL REPRODUCCIONES", True, (0, 255, 255)), (40, y_cont))
        surface.blit(self.fuente.render(str(total), True, (255, 255, 255)), (365, y_cont))
        self.render_item(surface, 2, "CARPETA CONTENIDOS", 'SISTEMA', 'ruta_contenidos')
        for i, campo in enumerate(self.gestor.campos_teclas):
            self.render_item(surface, i + 3, f"TECLA {campo.upper()}", 'TECLAS', campo)

    def render_item(self, surface, index, label, seccion, clave):
        y = 35 + (index * 45)
        sel = (self.fila_seleccionada == index)
        color = (255, 255, 0) if sel else (200, 200, 200)
        surface.blit(self.fuente.render(label, True, color), (40, y))
        pygame.draw.rect(surface, (45, 45, 60), (350, y-5, 360, 30))
        if sel and self.editando:
            if self.escuchando_tecla: val, col = ">>> PULSA UNA TECLA <<<", (255, 165, 0)
            else:
                lista = self.opciones_modo if index == 0 else self.gestor.lista_maestra
                val, col = f"< {lista[self.columna_combo % len(lista)]} >", (0, 255, 0)
        else:
            val, col = self.gestor.config[seccion].get(clave, "N/A"), (255, 255, 255)
        surface.blit(self.fuente.render(str(val), True, col), (365, y))

    def pantalla_bloqueo(self, datos_hw):
        ventana_error = pygame.display.set_mode((800, 500))
        while True:
            ventana_error.fill((120, 0, 0)) 
            t1 = self.fuente_negrita.render("SISTEMA BLOQUEADO - SIN LICENCIA ACTIVA", True, (255, 255, 255))
            t2 = self.fuente.render(f"ID MAC: {datos_hw['mac']}", True, (255, 255, 0))
            t3 = self.fuente.render("PEDIR LICENCIA AL: 1121674227", True, (255, 255, 255))
            ventana_error.blit(t1, (400 - t1.get_width()//2, 150))
            ventana_error.blit(t2, (400 - t2.get_width()//2, 220))
            ventana_error.blit(t3, (400 - t3.get_width()//2, 300))
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            pygame.display.flip()