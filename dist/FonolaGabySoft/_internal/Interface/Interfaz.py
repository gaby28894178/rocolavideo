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
        self.escribiendo_texto = False # Para el nombre de la fonola
        self.opciones_modo = ["LIBRE", "CREDITO"]
        self.input_texto = "" # Buffer para el nombre

    def abrir(self):
        # Guardamos tamaño original para volver luego
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
                    # --- MODO ESCRITURA (Para el nombre) ---
                    if self.escribiendo_texto:
                        if event.key == pygame.K_RETURN:
                            self.gestor.guardar('SISTEMA', 'nombre_fonola', self.input_texto)
                            self.escribiendo_texto = self.editando = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_texto = self.input_texto[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            self.escribiendo_texto = self.editando = False
                        else:
                            if len(self.input_texto) < 25: # Límite de caracteres
                                self.input_texto += event.unicode.upper()
                        continue

                    # --- MODO ESCUCHA TECLA (Para mapeo de botones) ---
                    if self.escuchando_tecla:
                        nombre = pygame.key.name(event.key).upper()
                        idx = self.fila_seleccionada - 4 # Ajustado por nueva fila
                        if idx >= 0: self.gestor.guardar('TECLAS', self.gestor.campos_teclas[idx], nombre)
                        self.escuchando_tecla = self.editando = False
                        continue

                    if event.key == pygame.K_F10 and not self.editando: running = False
                    
                    elif not self.editando:
                        total_filas = 4 + len(self.gestor.campos_teclas)
                        if event.key == pygame.K_UP: self.fila_seleccionada = (self.fila_seleccionada - 1) % total_filas
                        elif event.key == pygame.K_DOWN: self.fila_seleccionada = (self.fila_seleccionada + 1) % total_filas
                        elif event.key == pygame.K_RETURN:
                            # RESET DE REPRODUCCIONES (Fila 2)
                            if self.fila_seleccionada == 2:
                                self.gestor.resetear_reproducciones()
                            else:
                                self.editando = True
                                self.columna_combo = 0
                                if self.fila_seleccionada == 0: # Nombre
                                    self.escribiendo_texto = True
                                    self.input_texto = self.gestor.config['SISTEMA'].get('nombre_fonola', '')

                    else: # MODO EDICIÓN COMBO
                        if event.key == pygame.K_ESCAPE: self.editando = False
                        elif event.key == pygame.K_LEFT: self.columna_combo -= 1
                        elif event.key == pygame.K_RIGHT: self.columna_combo += 1
                        elif event.key == pygame.K_RETURN:
                            if self.fila_seleccionada == 1: # Modo Libre/Credito
                                self.gestor.guardar('SISTEMA', 'estado_rocola', self.opciones_modo[self.columna_combo % 2])
                                self.editando = False
                            elif self.fila_seleccionada >= 4: # Teclas
                                sel = self.gestor.lista_maestra[self.columna_combo % len(self.gestor.lista_maestra)]
                                if sel == "MODO ESCUCHA": self.escuchando_tecla = True
                                else:
                                    self.gestor.guardar('TECLAS', self.gestor.campos_teclas[self.fila_seleccionada-4], sel)
                                    self.editando = False
            
            pygame.display.flip()
        
        # Al salir, restauramos la resolución original
        pygame.display.set_mode((res_x, res_y))

    def dibujar_panel(self, surface):
        # 0. Nombre de la Fonola
        self.render_item(surface, 0, "NOMBRE DE FONOLA", 'SISTEMA', 'nombre_fonola')
        
        # 1. Modo
        self.render_item(surface, 1, "MODO REPRODUCCIÓN", 'SISTEMA', 'estado_rocola')
        
        # 2. Estadísticas (Especial: presiona Enter para reset)
        y_stats = 35 + (2 * 45)
        sel_stats = (self.fila_seleccionada == 2)
        col_stats = (255, 255, 0) if sel_stats else (0, 255, 255)
        surface.blit(self.fuente.render("TOTAL REPRODUCCIONES", True, col_stats), (40, y_stats))
        total = self.gestor.config['ESTADISTICAS'].get('total_reproducciones', '0')
        txt_stats = f"{total} (ENTER PARA RESET)" if sel_stats else str(total)
        surface.blit(self.fuente.render(txt_stats, True, (255, 255, 255)), (365, y_stats))

        # 3. Carpeta
        self.render_item(surface, 3, "CARPETA CONTENIDOS", 'SISTEMA', 'ruta_contenidos')

        # 4+. Teclas
        for i, campo in enumerate(self.gestor.campos_teclas):
            self.render_item(surface, i + 4, f"TECLA {campo.upper()}", 'TECLAS', campo)

    def render_item(self, surface, index, label, seccion, clave):
        y = 35 + (index * 45)
        sel = (self.fila_seleccionada == index)
        color = (255, 255, 0) if sel else (200, 200, 200)
        surface.blit(self.fuente.render(label, True, color), (40, y))
        
        pygame.draw.rect(surface, (45, 45, 60), (350, y-5, 360, 30))
        
        if sel and self.editando:
            if self.escribiendo_texto:
                val, col = self.input_texto + "|", (255, 255, 0)
            elif self.escuchando_tecla:
                val, col = ">>> PULSA UNA TECLA <<<", (255, 165, 0)
            else:
                lista = self.opciones_modo if index == 1 else self.gestor.lista_maestra
                val, col = f"< {lista[self.columna_combo % len(lista)]} >", (0, 255, 0)
        else:
            val, col = self.gestor.config[seccion].get(clave, "N/A"), (255, 255, 255)
        
        surface.blit(self.fuente.render(str(val), True, col), (365, y))

    # (El resto de métodos como loader y pantalla_bloqueo quedan igual)
    def mostrar_loader(self, surface, ruta_etiqueta, tiempo_ms=5000):
        # ... (Mantener igual que antes) ...
        pass
    
    def pantalla_bloqueo(self, datos_hw):
        # ... (Mantener igual que antes) ...
        pass