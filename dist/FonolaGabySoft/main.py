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
    try:
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
            comando = f'pythonw.exe "{ruta_script}"' if ruta_script.lower().endswith(".py") else f'"{ruta_script}"'
            reg.SetValueEx(key, nombre_app, 0, reg.REG_SZ, comando)
        else:
            try: reg.DeleteValue(key, nombre_app)
            except OSError: pass
        reg.CloseKey(key)
    except Exception as e:
        print(f"[CONFIG] Error en auto-inicio: {e}")

def main():
    pygame.init()

    # 1. Cargar Configuración
    gestor_teclas = GestorTeclas()
    conf_sis = gestor_teclas.config['SISTEMA']
    
    # 2. Resolución y Ventana (IMPORTANTE: Crear la ventana ANTES del loader)
    res_x = int(conf_sis.get('res_x', 1024))
    res_y = int(conf_sis.get('res_y', 720))
    es_fullscreen = conf_sis.get('fullscreen', 'NO').upper() == 'SI'

    if es_fullscreen:
        screen = pygame.display.set_mode((res_x, res_y), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((res_x, res_y))
    
    pygame.display.set_caption(conf_sis.get('nombre_fonola', 'FONOLA GABYSOFT'))

    # 3. Icono
    try:
        ruta_ico = recurso_path("Interface/img/vinilo.png")
        if os.path.exists(ruta_ico):
            pygame.display.set_icon(pygame.image.load(ruta_ico))
    except: pass

    # 4. Validación de Licencia
    recolector = RecolectorHardware()
    datos_pc = recolector.obtener_datos()
    validador = GestorLicencia('url.ini') 
    licencia_ok = validador.validar_remoto(datos_pc)

    interfaz = VentanaConfig(gestor_teclas)

    # --- AQUÍ ESTÁ EL CAMBIO CLAVE ---
    if licencia_ok:
        # Forzamos la ruta del logo
        ruta_img_loader = recurso_path("Interface/img/image_1.png")
        
        # LLAMADA AL LOADER (Aseguramos que screen ya existe)
        print("Iniciando Loader...")
        interfaz.mostrar_loader(screen, ruta_img_loader, 15000) 
        print("Loader finalizado.")
    else:
        interfaz.pantalla_bloqueo(datos_pc)
        return

    # 5. Carga de música (Esto pasa DESPUÉS del loader)
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
                    interfaz.abrir() 
                    gestor_teclas.cargar_config()
                    # (Resto de actualizaciones de config...)

        explorador.dibujar_grilla()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()