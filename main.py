import pygame
import sys
from Logic.Hardware import RecolectorHardware
from Logic.Gestor_licencia import GestorLicencia
from Logic.Gestor_teclas import GestorTeclas
from Interface.Interfaz import VentanaConfig
from Logic.Biblioteca import MotorBiblioteca
from Interface.Explorador import ExploradorMultimedia

def main():
    pygame.init()
    RES_X, RES_Y = 1224, 768
    screen = pygame.display.set_mode((RES_X, RES_Y))
    pygame.display.set_caption("FONOLA GABYSOFT")

    recolector = RecolectorHardware()
    datos_pc = recolector.obtener_datos()
    validador = GestorLicencia('url.ini')
    licencia_ok = validador.validar_remoto(datos_pc)

    gestor_teclas = GestorTeclas()
    interfaz = VentanaConfig(gestor_teclas)

    if licencia_ok:
        interfaz.mostrar_loader(screen, "Interface/img/image_1.png", 15000)
    else:
        interfaz.pantalla_bloqueo(datos_pc)
        return

    biblioteca = MotorBiblioteca()
    ruta_musica = gestor_teclas.config['SISTEMA'].get('ruta_contenidos', 'C:/musica') 
    coleccion_cds = biblioteca.cargar_coleccion(ruta_musica)
    
    explorador = ExploradorMultimedia(screen, gestor_teclas, coleccion_cds)

    clock = pygame.time.Clock()

    while True:
        eventos = pygame.event.get()
        explorador.manejar_eventos(eventos)
        
        for event in eventos:
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F10: 
                    interfaz.abrir()
                    screen = pygame.display.set_mode((RES_X, RES_Y))
                    ruta_n = gestor_teclas.config['SISTEMA'].get('ruta_contenidos', 'C:/musica')
                    explorador.coleccion = biblioteca.cargar_coleccion(ruta_n)

        explorador.dibujar_grilla()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()