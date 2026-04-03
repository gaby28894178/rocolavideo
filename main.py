import pygame
import sys
import os
import winreg as reg
from Logic.Hardware import RecolectorHardware
from Logic.Gestor_licencia import GestorLicencia
from Logic.Gestor_teclas import GestorTeclas
from Interface.Interfaz import VentanaConfig
from Logic.Biblioteca import MotorBiblioteca
from Interface.Explorador import ExploradorMultimedia

def recurso_path(relative_path):
    """ Obtiene la ruta absoluta de los recursos para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def configurar_auto_inicio(activar):
    nombre_app = "FonolaGabySoft"
    ruta_script = os.path.abspath(sys.argv[0])
    llave_ruta = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, llave_ruta, 0, reg.KEY_SET_VALUE)
        if activar == "SI":
            if ruta_script.lower().endswith(".py"):
                comando = f'pythonw.exe "{ruta_script}"'
            else:
                comando = f'"{ruta_script}"'
            reg.SetValueEx(key, nombre_app, 0, reg.REG_SZ, comando)
        else:
            try: reg.DeleteValue(key, nombre_app)
            except OSError: pass
        reg.CloseKey(key)
    except Exception as e:
        print(f"[CONFIG] Error en auto-inicio: {e}")

def main():
    pygame.init()

    # 1. Cargar Configuración General
    gestor_teclas = GestorTeclas()
    conf_sis = gestor_teclas.config['SISTEMA']
    
    # 2. Configurar Icono de la App (ARREGLADO CON RECURSO_PATH)
    try:
        # Usamos el path corregido para que el EXE encuentre la imagen interna
        ruta_icono = recurso_path("Interface/img/vinilo.png")
        icono = pygame.image.load(ruta_icono)
        pygame.display.set_icon(icono)
    except Exception as e:
        print(f"Error cargando icono: {e}")
    
    # 3. Auto-inicio
    configurar_auto_inicio(conf_sis.get('auto_inicio', 'NO').upper())

    # 4. Configurar Pantalla Inicial
    res_x = int(conf_sis.get('res_x', 1024))
    res_y = int(conf_sis.get('res_y', 720))
    es_fullscreen = conf_sis.get('fullscreen', 'NO').upper() == 'SI'

    if es_fullscreen:
        screen = pygame.display.set_mode((res_x, res_y), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((res_x, res_y))
    
    # --- TÍTULO DINÁMICO ---
    nombre_app = conf_sis.get('nombre_fonola', 'FONOLA GABYSOFT')
    pygame.display.set_caption(nombre_app)

    # 5. Validación de Licencia (Los .ini se quedan afuera del EXE para ser editables)
    recolector = RecolectorHardware()
    datos_pc = recolector.obtener_datos()
    validador = GestorLicencia('url.ini') 
    licencia_ok = validador.validar_remoto(datos_pc)

    interfaz = VentanaConfig(gestor_teclas)

    if licencia_ok:
        # ARREGLADO CON RECURSO_PATH para el loader
        ruta_loader = recurso_path("Interface/img/image_1.png")
        interfaz.mostrar_loader(screen, ruta_loader, 5000)
    else:
        interfaz.pantalla_bloqueo(datos_pc)
        return

    # 6. Carga de Biblioteca
    biblioteca = MotorBiblioteca()
    ruta_musica = conf_sis.get('ruta_contenidos', 'C:/musica') 
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
                    # --- ABRIR CONFIGURACIÓN ---
                    interfaz.abrir() 
                    
                    # --- ACTUALIZAR CAMBIOS AL VOLVER ---
                    gestor_teclas.cargar_config()
                    
                    # 1. Actualizar Título
                    nombre_nuevo = gestor_teclas.config['SISTEMA'].get('nombre_fonola', 'FONOLA GABYSOFT')
                    pygame.display.set_caption(nombre_nuevo)
                    
                    # 2. Actualizar Resolución
                    nx = int(gestor_teclas.config['SISTEMA'].get('res_x', 1024))
                    ny = int(gestor_teclas.config['SISTEMA'].get('res_y', 720))
                    if nx != res_x or ny != res_y:
                        res_x, res_y = nx, ny
                        if gestor_teclas.config['SISTEMA'].get('fullscreen') == 'SI':
                            screen = pygame.display.set_mode((res_x, res_y), pygame.FULLSCREEN)
                        else:
                            screen = pygame.display.set_mode((res_x, res_y))
                        explorador.surface = screen

                    # 3. Sincronizar ruta de música
                    nueva_ruta = gestor_teclas.config['SISTEMA'].get('ruta_contenidos')
                    if nueva_ruta != ruta_musica:
                        ruta_musica = nueva_ruta
                        explorador.coleccion = biblioteca.cargar_coleccion(ruta_musica)

        explorador.dibujar_grilla()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()